#!/usr/bin/env python3
"""
Simple Coffee Shop - Terminal User Interface (TUI)
Author: Hermes
Location: /mnt/c/Phurin-reabroi/PythonCode/SimpleCoffeeShop/coffee_shop_tui.py

A beautiful, easy-to-navigate, and interactive terminal-based coffee shop system.
Features:
- Main menu with description, price, and category.
- Cart management (add, edit quantities, remove).
- Coupon code system (apply existing coupons, redeem for discounts).
- Checkout flow: validates customer email, issues a 15% discount coupon for NEXT purchase, and saves to coupons.json.
- Beautiful receipt rendering.
- Admin panel to inspect active coupons and checkout logs.
"""

import os
import json
import re
import random
from datetime import datetime

# ==========================================
# COLOR CONSTANTS (ANSI ESCAPE CODES)
# ==========================================
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# Text Colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Background Colors (for highlights)
BG_CYAN = "\033[46m"
BG_BLACK = "\033[40m"

# ==========================================
# COFFEE SHOP DATA & CORE CONFIGURATION
# ==========================================
MENU = {
    "1": {"name": "Espresso", "price": 2.50, "desc": "Rich, bold, single shot of pure espresso"},
    "2": {"name": "Americano", "price": 3.00, "desc": "Smooth, bold espresso diluted with hot water"},
    "3": {"name": "Latte", "price": 4.00, "desc": "Creamy espresso with steamed milk and light foam"},
    "4": {"name": "Cappuccino", "price": 4.00, "desc": "Perfect balance of espresso, milk, and dense foam"},
    "5": {"name": "Mocha", "price": 4.50, "desc": "Espresso with steamed milk and rich chocolate syrup"},
    "6": {"name": "Macchiato", "price": 3.50, "desc": "Espresso 'marked' with a dollop of frothy milk"},
    "7": {"name": "Flat White", "price": 4.25, "desc": "Velvety microfoam milk poured over a double shot"},
    "8": {"name": "Iced Latte", "price": 4.50, "desc": "Refreshing chilled latte served over ice"},
    "9": {"name": "Cold Brew", "price": 3.75, "desc": "Smooth, low-acid, slow-steeped iced coffee"},
    "10": {"name": "Vanilla Latte", "price": 4.75, "desc": "Classic latte sweetened with premium vanilla syrup"}
}

COUPONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coupons.json")
SALES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_history.json")

# ==========================================
# UTILITY FUNCTIONS
# ==========================================
def clear_screen():
    """Clear terminal screen depending on the OS"""
    os.system("cls" if os.name == "nt" else "clear")

def format_currency(amount):
    """Format float amount as standard dollar representation"""
    return f"${amount:.2f}"

def validate_email(email):
    """Verify email format using standard regex"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def generate_coupon_code():
    """Generate a unique coupon code for 15% discount"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "HERMES-" + "".join(random.choice(chars) for _ in range(8))

# ==========================================
# COUPON & SALES FILE MANAGEMENT
# ==========================================
def load_json_file(file_path, default_data):
    """Safe wrapper for loading JSON data"""
    if not os.path.exists(file_path):
        return default_data
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_data

def save_json_file(file_path, data):
    """Safe wrapper for saving JSON data"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"{RED}Error saving data to {file_path}: {e}{RESET}")
        return False

# ==========================================
# MAIN APPLICATION STATE & LOGIC
# ==========================================
class CoffeeShopApp:
    def __init__(self):
        self.cart = {}  # Format: {item_id: quantity}
        self.applied_coupon = None  # Format: {"code": str, "discount_pct": int}
        self.active_coupons = load_json_file(COUPONS_FILE, {})
        self.sales_history = load_json_file(SALES_FILE, [])

    def add_to_cart(self, item_id, qty):
        """Add or update an item in the cart"""
        if item_id not in MENU:
            return False
        if qty <= 0:
            return False
        
        self.cart[item_id] = self.cart.get(item_id, 0) + qty
        return True

    def update_cart_qty(self, item_id, qty):
        """Update cart quantity, remove if quantity <= 0"""
        if item_id not in self.cart:
            return False
        if qty <= 0:
            del self.cart[item_id]
        else:
            self.cart[item_id] = qty
        return True

    def calculate_subtotal(self):
        """Sum of price * quantity for all items in cart"""
        return sum(MENU[item_id]["price"] * qty for item_id, qty in self.cart.items())

    def apply_coupon(self, code):
        """Apply a coupon code if valid and unused"""
        code = code.strip().upper()
        if code in self.active_coupons:
            coupon = self.active_coupons[code]
            if not coupon.get("used", False):
                self.applied_coupon = {
                    "code": code,
                    "discount_pct": coupon.get("discount_pct", 15)
                }
                return True, coupon.get("discount_pct", 15)
            else:
                return False, "This coupon code has already been redeemed."
        return False, "Invalid coupon code."

    def finalize_checkout(self, email):
        """Finalize purchase, log sale, use applied coupon, generate new coupon"""
        subtotal = self.calculate_subtotal()
        discount = 0.0
        
        if self.applied_coupon:
            discount_pct = self.applied_coupon["discount_pct"]
            discount = round(subtotal * (discount_pct / 100), 2)
            # Mark applied coupon as used
            code = self.applied_coupon["code"]
            if code in self.active_coupons:
                self.active_coupons[code]["used"] = True
                self.active_coupons[code]["used_by"] = email
                self.active_coupons[code]["used_at"] = datetime.now().isoformat()

        total = max(0.0, subtotal - discount)
        
        # Issue next-purchase coupon for 15% discount
        new_coupon = generate_coupon_code()
        self.active_coupons[new_coupon] = {
            "discount_pct": 15,
            "issued_to": email,
            "issued_at": datetime.now().isoformat(),
            "used": False
        }
        
        # Record sale
        sale_record = {
            "timestamp": datetime.now().isoformat(),
            "customer_email": email,
            "items": {MENU[item_id]["name"]: qty for item_id, qty in self.cart.items()},
            "subtotal": subtotal,
            "discount_applied": discount,
            "applied_coupon": self.applied_coupon["code"] if self.applied_coupon else None,
            "total_paid": total,
            "new_coupon_issued": new_coupon
        }
        self.sales_history.append(sale_record)
        
        # Save persistent states
        save_json_file(COUPONS_FILE, self.active_coupons)
        save_json_file(SALES_FILE, self.sales_history)
        
        # Reset cart and coupon state
        cart_copy = dict(self.cart)
        applied_coupon_copy = dict(self.applied_coupon) if self.applied_coupon else None
        
        self.cart = {}
        self.applied_coupon = None
        
        return {
            "cart": cart_copy,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "new_coupon": new_coupon,
            "applied_coupon": applied_coupon_copy,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# ==========================================
# UI RENDERING & USER INPUTS
# ==========================================
class CoffeeShopTUI:
    def __init__(self):
        self.app = CoffeeShopApp()

    def print_banner(self):
        """Display styled header"""
        print(f"{YELLOW}{BOLD}" + "═" * 60)
        print("          ⚡ WELCOME TO THE HERMES COFFEE HOUSE ⚡")
        print("              Pure Beans • Rich Brews • Cozy TUI")
        print("═" * 60 + f"{RESET}")

    def show_main_menu(self):
        """Displays choices for navigating the app"""
        clear_screen()
        self.print_banner()
        print(f"\n{BOLD}{CYAN}Please choose an option to navigate:{RESET}")
        print(f"  {BOLD}{GREEN}1.{RESET} Browse Coffee Menu & Place Order")
        print(f"  {BOLD}{GREEN}2.{RESET} View Cart & Modify Quantities")
        print(f"  {BOLD}{GREEN}3.{RESET} Redeem Coupon Code")
        print(f"  {BOLD}{GREEN}4.{RESET} Checkout & Generate Next-Purchase Coupon")
        print(f"  {BOLD}{GREEN}5.{RESET} Admin Portal (View Coupons & Sales History)")
        print(f"  {BOLD}{RED}6.{RESET} Exit")
        print(f"\n" + "─" * 60)
        
        # Quick status bar
        cart_count = sum(self.app.cart.values())
        coupon_status = f"{GREEN}Applied ({self.app.applied_coupon['code']} -{self.app.applied_coupon['discount_pct']}%){RESET}" if self.app.applied_coupon else f"{RED}None{RESET}"
        print(f"  Cart items: {YELLOW}{cart_count}{RESET} | Coupon: {coupon_status} | Subtotal: {YELLOW}{format_currency(self.app.calculate_subtotal())}{RESET}")
        print("─" * 60)

    def view_coffee_menu(self):
        """Renders coffee items, lets customer add to cart"""
        while True:
            clear_screen()
            self.print_banner()
            print(f"\n{BOLD}{MAGENTA}☕ OUR DELICIOUS MENU ☕{RESET}")
            print(f"{'No.':<4} | {'Beverage Name':<16} | {'Price':<7} | {'Description':<30}")
            print("─" * 60)
            for cid, info in MENU.items():
                print(f"{BOLD}{CYAN}{cid:>2}{RESET}  | {BOLD}{WHITE}{info['name']:<16}{RESET} | {YELLOW}{format_currency(info['price']):<7}{RESET} | {info['desc']:<30}")
            print("─" * 60)
            print(f"Type {BOLD}{YELLOW}item number{RESET} to order, or press {BOLD}{RED}ENTER{RESET} to go back to main menu.")
            
            choice = input(f"\n{BOLD}{CYAN}Selection 👉 {RESET}").strip()
            if not choice:
                break
            
            if choice in MENU:
                item = MENU[choice]
                qty_input = input(f"How many cups of {BOLD}{item['name']}{RESET} would you like? (Default: 1): ").strip()
                if qty_input == "":
                    qty = 1
                else:
                    try:
                        qty = int(qty_input)
                        if qty <= 0:
                            print(f"{RED}Invalid quantity. Must be at least 1.{RESET}")
                            input("\nPress ENTER to continue...")
                            continue
                    except ValueError:
                        print(f"{RED}Please enter a valid whole number.{RESET}")
                        input("\nPress ENTER to continue...")
                        continue
                
                self.app.add_to_cart(choice, qty)
                print(f"\n{GREEN}Added {BOLD}{qty}x {item['name']}{RESET} to your cart! 🎉")
                input("\nPress ENTER to continue shopping...")
            else:
                print(f"{RED}Item '{choice}' does not exist on our menu.{RESET}")
                input("\nPress ENTER to try again...")

    def view_cart(self):
        """Display current items in cart and allow modification"""
        while True:
            clear_screen()
            self.print_banner()
            print(f"\n{BOLD}{MAGENTA}🛒 YOUR SHOPPING CART 🛒{RESET}")
            
            if not self.app.cart:
                print(f"\n{YELLOW}Your shopping cart is empty.{RESET}")
                print("Go to Option 1 to add some delicious coffee items!")
                print("─" * 60)
                input("\nPress ENTER to return to main menu...")
                break
                
            print(f"{'No.':<4} | {'Beverage Name':<16} | {'Qty':<5} | {'Price':<7} | {'Total Price':<10}")
            print("─" * 60)
            
            index = 1
            idx_to_cid = {}
            for cid, qty in self.app.cart.items():
                item = MENU[cid]
                total_item_price = item["price"] * qty
                print(f"{BOLD}{CYAN}{index:>2}{RESET}  | {WHITE}{item['name']:<16}{RESET} | {qty:<5} | {format_currency(item['price']):<7} | {YELLOW}{format_currency(total_item_price):<10}{RESET}")
                idx_to_cid[str(index)] = cid
                index += 1
                
            print("─" * 60)
            subtotal = self.app.calculate_subtotal()
            print(f"Subtotal: {BOLD}{YELLOW}{format_currency(subtotal)}{RESET}")
            
            if self.app.applied_coupon:
                disc_pct = self.app.applied_coupon["discount_pct"]
                discount_val = subtotal * (disc_pct / 100)
                print(f"Coupon Discount ({self.app.applied_coupon['code']} -{disc_pct}%): {BOLD}{RED}-{format_currency(discount_val)}{RESET}")
                print(f"Total: {BOLD}{GREEN}{format_currency(subtotal - discount_val)}{RESET}")
            
            print("\nOptions:")
            print(f"  • To edit an item's quantity: Type the {BOLD}{CYAN}Item Line No.{RESET} (1, 2...)")
            print(f"  • Press {BOLD}{RED}ENTER{RESET} to return to main menu")
            
            choice = input(f"\n{BOLD}{CYAN}Selection 👉 {RESET}").strip()
            if not choice:
                break
                
            if choice in idx_to_cid:
                cid = idx_to_cid[choice]
                item_name = MENU[cid]["name"]
                new_qty_str = input(f"Enter new quantity for {BOLD}{item_name}{RESET} (Type {BOLD}0{RESET} to remove item): ").strip()
                try:
                    new_qty = int(new_qty_str)
                    if new_qty < 0:
                        print(f"{RED}Quantity cannot be negative.{RESET}")
                        input("\nPress ENTER to continue...")
                        continue
                    self.app.update_cart_qty(cid, new_qty)
                    print(f"\n{GREEN}Cart updated successfully!{RESET}")
                    input("\nPress ENTER to refresh cart...")
                except ValueError:
                    print(f"{RED}Please enter a valid integer.{RESET}")
                    input("\nPress ENTER to continue...")
            else:
                print(f"{RED}Invalid line number.{RESET}")
                input("\nPress ENTER to try again...")

    def apply_coupon_screen(self):
        """Menu option to enter a coupon code"""
        clear_screen()
        self.print_banner()
        print(f"\n{BOLD}{MAGENTA}🎫 REDEEM COUPON CODE 🎫{RESET}")
        
        if self.app.applied_coupon:
            print(f"\nYou already have a coupon applied: {GREEN}{self.app.applied_coupon['code']}{RESET} (-{self.app.applied_coupon['discount_pct']}%).")
            change = input("Would you like to overwrite it with a new one? (y/n): ").strip().lower()
            if change != 'y':
                return
        
        code = input(f"\nEnter coupon code: {BOLD}").strip()
        if not code:
            return
            
        success, info = self.app.apply_coupon(code)
        if success:
            print(f"\n{GREEN}Success! Coupon {BOLD}{code.upper()}{RESET}{GREEN} applied. You saved {BOLD}{info}%{RESET}{GREEN} on your order!{RESET}")
        else:
            print(f"\n{RED}Error: {info}{RESET}")
        input("\nPress ENTER to continue...")

    def checkout_screen(self):
        """Checkout screen to review the cart, request email, print receipt & coupon"""
        clear_screen()
        self.print_banner()
        print(f"\n{BOLD}{MAGENTA}💸 CHECKOUT & RECEIPT GENERATOR 💸{RESET}")
        
        if not self.app.cart:
            print(f"\n{RED}Cannot checkout: Your shopping cart is empty.{RESET}")
            print("Please add items to your cart before checking out.")
            input("\nPress ENTER to return to main menu...")
            return
            
        # Preview Order
        print(f"\n{BOLD}ORDER SUMMARY:{RESET}")
        print("─" * 40)
        for cid, qty in self.app.cart.items():
            item = MENU[cid]
            print(f"  • {qty}x {item['name']:<18} @ {format_currency(item['price'])} = {format_currency(item['price'] * qty)}")
        print("─" * 40)
        
        subtotal = self.app.calculate_subtotal()
        print(f"  Subtotal:         {format_currency(subtotal)}")
        discount = 0.0
        if self.app.applied_coupon:
            disc_pct = self.app.applied_coupon["discount_pct"]
            discount = subtotal * (disc_pct / 100)
            print(f"  Coupon Discount:  {RED}-{format_currency(discount)} ({self.app.applied_coupon['code']}){RESET}")
        print(f"  {BOLD}TOTAL DUE:        {GREEN}{format_currency(subtotal - discount)}{RESET}")
        print("─" * 40)
        
        # Email prompting
        print(f"\n{YELLOW}Please enter your email to complete checkout.{RESET}")
        print("We will instantly issue a 15% discount coupon for your NEXT purchase!")
        
        while True:
            email = input(f"\n{BOLD}{CYAN}Customer Email 👉 {RESET}").strip()
            if not email:
                print(f"{RED}Email is required to checkout and generate your next coupon.{RESET}")
                choice = input("Type 'x' to cancel checkout, or press ENTER to retry: ").strip().lower()
                if choice == 'x':
                    return
                continue
                
            if validate_email(email):
                break
            else:
                print(f"{RED}Invalid email format (e.g. name@domain.com). Please try again.{RESET}")
                
        # Process order
        receipt = self.app.finalize_checkout(email)
        
        # Render the Receipt beautifully
        clear_screen()
        print("\n" + "═" * 45)
        print("         ⚡ HERMES COFFEE HOUSE RECEIPT ⚡")
        print(f"         Date: {receipt['date']}")
        print(f"         Customer: {email}")
        print("═" * 45)
        print(f" {'Item Name':<18} | {'Qty':<4} | {'Unit':<5} | {'Total':<8}")
        print("─" * 45)
        
        for cid, qty in receipt["cart"].items():
            item = MENU[cid]
            line_total = item["price"] * qty
            print(f" {item['name']:<18} | {qty:<4} | {item['price']:<5.2f} | {line_total:<8.2f}")
            
        print("─" * 45)
        print(f" Subtotal:                              ${receipt['subtotal']:.2f}")
        if receipt["discount"] > 0:
            coupon_code = receipt["applied_coupon"]["code"]
            discount_pct = receipt["applied_coupon"]["discount_pct"]
            print(f" Coupon ({coupon_code} -{discount_pct}%):             -${receipt['discount']:.2f}")
        print(f" {BOLD}TOTAL PAID:                             ${receipt['total']:.2f}{RESET}")
        print("═" * 45)
        print("    🎁 YOUR EXCLUSIVE NEXT-PURCHASE COUPON 🎁")
        print(f"        CODE:  {BOLD}{YELLOW}{receipt['new_coupon']}{RESET}")
        print("        VALUE: 15% OFF (Your Next Order)")
        print("        Saved to coupons.json for next time!")
        print("═" * 45)
        print("\nThank you for choosing Hermes Coffee House! ☕✨")
        input("\nPress ENTER to return to the main menu...")

    def admin_portal(self):
        """Admin view to inspect registered coupons and receipt logs"""
        while True:
            clear_screen()
            self.print_banner()
            print(f"\n{BOLD}{RED}⚙️  ADMIN PORTAL ⚙️{RESET}")
            print("  1. View Active and Used Coupons")
            print("  2. View Sales History & Earnings Logs")
            print("  3. Exit Admin Portal")
            print("─" * 60)
            
            choice = input(f"{BOLD}{CYAN}Admin Choice 👉 {RESET}").strip()
            if choice == "3" or not choice:
                break
                
            if choice == "1":
                clear_screen()
                self.print_banner()
                print(f"\n{BOLD}{MAGENTA}📋 COUPONS DATABASE LOGS 📋{RESET}")
                coupons = self.app.active_coupons
                if not coupons:
                    print(f"{YELLOW}No coupons currently registered in system.{RESET}")
                else:
                    print(f"{'Coupon Code':<16} | {'Discount':<8} | {'Issued To':<25} | {'Status':<10}")
                    print("─" * 70)
                    for code, data in coupons.items():
                        status = f"{RED}USED{RESET}" if data.get("used", False) else f"{GREEN}ACTIVE{RESET}"
                        print(f"{BOLD}{WHITE}{code:<16}{RESET} | {data.get('discount_pct', 15):<6}% | {data.get('issued_to', 'System'):<25} | {status:<10}")
                print("─" * 70)
                input("\nPress ENTER to go back...")
                
            elif choice == "2":
                clear_screen()
                self.print_banner()
                print(f"\n{BOLD}{MAGENTA}📈 SALES TRANSACTION HISTORY 📈{RESET}")
                sales = self.app.sales_history
                if not sales:
                    print(f"{YELLOW}No sales transactions recorded yet.{RESET}")
                else:
                    total_earnings = sum(sale["total_paid"] for sale in sales)
                    print(f"Total Sales: {BOLD}{GREEN}{format_currency(total_earnings)}{RESET}")
                    print(f"Total Receipts Issued: {len(sales)}")
                    print("─" * 70)
                    for i, sale in enumerate(sales, 1):
                        date_str = sale["timestamp"][:19].replace("T", " ")
                        print(f"{BOLD}Transaction #{i}{RESET} [{date_str}] - Customer: {CYAN}{sale['customer_email']}{RESET}")
                        print(f"  Items: {sale['items']}")
                        print(f"  Paid: {GREEN}{format_currency(sale['total_paid'])}{RESET} (Subtotal: {format_currency(sale['subtotal'])} | Discount: {format_currency(sale['discount_applied'])})")
                        print("─" * 70)
                input("\nPress ENTER to go back...")
            else:
                print(f"{RED}Invalid Option.{RESET}")
                input("\nPress ENTER to retry...")

    def run(self):
        """Main application lifecycle loop"""
        while True:
            self.show_main_menu()
            choice = input(f"{BOLD}{CYAN}Select an option (1-6) 👉 {RESET}").strip()
            
            if choice == "1":
                self.view_coffee_menu()
            elif choice == "2":
                self.view_cart()
            elif choice == "3":
                self.apply_coupon_screen()
            elif choice == "4":
                self.checkout_screen()
            elif choice == "5":
                self.admin_portal()
            elif choice == "6" or choice.lower() in ["exit", "quit"]:
                clear_screen()
                print("\n" + "═" * 45)
                print("      Thank you for visiting Hermes Coffee!")
                print("            Have a highly productive day! ☕")
                print("═" * 45 + "\n")
                break
            else:
                print(f"\n{RED}Invalid Choice. Please type a number between 1 and 6.{RESET}")
                input("\nPress ENTER to try again...")

if __name__ == "__main__":
    tui = CoffeeShopTUI()
    tui.run()
