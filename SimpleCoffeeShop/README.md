# ☕ Simple Coffee Shop TUI

Welcome to **Simple Coffee Shop**, a beautifully styled and interactive **Terminal User Interface (TUI)** application written in Python.

It is designed to be highly intuitive, portable, and extremely easy to navigate, with clean, modular, and well-commented code.

## 🌟 Key Features

1. **Interactive Menu**: View coffee selections with live-calculated totals, detailed descriptions, and standard pricing.
2. **Cart Management**: Add multiple coffees, customize and edit quantities, or remove items directly in an elegant cart view.
3. **Coupon Code System**: 
   - Apply existing discount coupon codes to save money during checkout.
   - Saves coupons to a local database (`coupons.json`) so they persist across sessions.
4. **Checkout Flow**: 
   - Requests a customer email (validates using safe regular expressions).
   - Generates a custom receipt printed like a real physical shop slip.
   - Instantly issues a **15% off next purchase discount code** for the email provided.
5. **Admin Portal**: Secret dashboard allowing admins/cashiers to:
   - View active and used coupon codes, including who used them and when.
   - View historical transactions and total earnings.

---

## 🚀 How to Run

Since the application only uses standard Python built-in modules (`os`, `json`, `re`, `random`, `datetime`), **no external libraries are required**! It runs anywhere seamlessly.

To launch the coffee shop:

```bash
cd /mnt/c/Phurin-reabroi/PythonCode/SimpleCoffeeShop/
python3 coffee_shop_tui.py
```

Or run directly if marked executable:
```bash
./coffee_shop_tui.py
```

---

## 📂 Project Structure

- `coffee_shop_tui.py` — The core executable application (Model-View-Controller pattern).
- `coupons.json` — Local persistent database storing generated coupon codes.
- `sales_history.json` — Database logging checkout transactions and total store metrics.
- `README.md` — This documentation file.

---

## 🎨 TUI Color Codes
The application uses pure, non-intrusive **ANSI Escape Sequences** for professional terminal-rendered styling, supportable on modern Linux, macOS, and WSL terminals.
