# Sikandar Furniture — Flask Store (with Login)

Python/Flask se bana hua furniture e-commerce site: product catalog, filters/sort,
shopping cart, **user login/register (with hashed passwords)**, checkout aur
order history — sab kuch is folder mein hai.

## Chalane ka tareeqa (Run it)

1. Python 3.9+ honi chahiye.
2. Terminal mein is folder ke andar jayein:
   ```bash
   cd sikandar-furniture-flask
   ```
3. (Recommended) virtual environment banayein:
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```
4. Dependencies install karein:
   ```bash
   pip install -r requirements.txt
   ```
5. App run karein:
   ```bash
   python app.py
   ```
6. Browser mein kholein: **http://127.0.0.1:5000**

Pehli baar run karne par `store.db` (SQLite database) khud-ba-khud ban jayegi
users aur orders store karne ke liye.

## Kya kya features hain

- **Register / Login / Logout** — passwords `werkzeug.security` se hash hoke
  save hote hain, plain text mein kabhi nahi.
- **Session-based cart** — guest bhi cart mein items add kar sakta hai; login
  sirf **checkout** ke waqt zaroori hai.
- **Checkout** — order database mein save hota hai, cart clear ho jata hai.
- **My Orders page** (`/account`) — login ke baad past orders dekh sakte hain.
- **Filters + sort** — category ke hisaab se aur price/rating se sort.
- **Product cards** — image, price, purani price (discount), rating, colors.
- Animations, responsive design, dark oak/sage theme.

## Files

```
app.py              -> Flask backend (routes, auth, cart API, DB)
requirements.txt    -> pip dependencies
templates/
  base.html          -> shared layout (nav, cart drawer, footer)
  index.html          -> homepage + product grid
  login.html / register.html
  account.html         -> order history
static/
  style.css
  script.js
store.db             -> auto-created SQLite database (users + orders)
```

## Zaroori note

`app.secret_key` abhi ek demo string hai (`app.py` ke top par) — agar yeh
site kahin real deploy karni ho to usay kisi random secret se replace kar
dein aur `debug=True` ko production mein `False` kar dein.
