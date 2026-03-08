Phase 1: Setup and Data Access Layer (15% marks) – Start Here
Focus on getting the database/models working so you can build on them. This is foundational and quick to implement.

Convert the notes into pip-installable format. Include: Django, djangorestframework, django-crispy-forms, crispy-bootstrap5 (for styling), requests (for currency API calls if needed, though rates are hardcoded).
Why: Needed for all layers. Run pip install -r requirements.txt after.
Validate: No errors on install.
Configure settings.py (Effort: 20 min)

Add installed apps: 'register', 'payapp', 'rest*framework', 'crispy_forms', 'crispy_bootstrap5'.
Set database to SQLite (default is fine).
Enable security: Add 'django.middleware.security.SecurityMiddleware', set SECURE_SSL_REDIRECT = True (for HTTPS in deployment), CSRF_COOKIE_SECURE = True, etc.
Configure Crispy Forms: CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5", CRISPY_TEMPLATE_PACK = "bootstrap5".
Why: Enables core Django features and security. Without this, nothing runs.
Validate: Run python [manage.py](http://\_vscodecontentref*/6) check – no errors.
Create models in payapp/models.py (Effort: 1-2 hours)

Extend Django's AbstractUser for a custom User model with fields: username, first*name, last_name, email, password, balance (DecimalField, default £500), currency (choices: GBP, USD, EUR).
Add Transaction model: fields like sender (ForeignKey to User), receiver, amount, currency, status (completed/pending), timestamp.
Add PaymentRequest model: similar to Transaction but for requests (with accept/reject status).
Use on_delete=models.CASCADE for relationships.
Why: Core data layer (15% marks). Supports all user/admin features.
Validate: Run python [manage.py](http://\_vscodecontentref*/7) makemigrations && python [manage.py](http://_vscodecontentref_/8) migrate – creates tables. Use Django admin to add test data.
Create initial admin user (Effort: 10 min)

In a migration or data fixture, create username: admin1, password: admin1 (as required).
Why: Security layer requirement (1% marks).
Validate: Login to admin panel works.
Phase 2: Business Logic and Presentation Layers (40% marks)
Build views and templates next—connect them to models for functionality.

Implement authentication views (Security Layer, 5% marks) (Effort: 30 min)

Use Django's built-in auth: Create registration/login/logout views in views.py.
On registration, set initial balance/currency.
Why: Required for all interactions.
Validate: Users can register, login, logout via URLs.
Create user views (Business Logic, 15% marks) (Effort: 2-3 hours)

Views in payapp/views.py: view_transactions, make_payment, request_payment, accept_reject_request.
Use @transaction.atomic for payments to ensure ACID.
Restrict to logged-in users with @login_required.
Why: Core user functionality.
Validate: Payments update balances correctly; no data loss on errors.
Create admin views (Business Logic, 5% marks) (Effort: 1 hour)

Views: view_all_users, view_all_transactions, register_admin.
Restrict to admins (use groups or a is_admin field).
Why: Admin features.
Validate: Admins see all data; can create other admins.
Create templates (Presentation Layer, 20% marks) (Effort: 3-4 hours)

In templates: HTML pages for all views (e.g., login.html, transactions.html, admin_dashboard.html).
Use Crispy Forms for forms, Bootstrap for styling (clean, consistent design).
Include navigation (URLConf rules in urls.py).
Add security pages (login, etc.).
Why: 10% for templates/views connection, 5% for validation/navigation, 5% for appearance.
Validate: Pages load correctly; navigation works; forms validate (e.g., required fields).
Set up URLs and access control (Security/Presentation, 4-5% marks) (Effort: 30 min)

In urls.py: Map views to paths (e.g., /login/, /payments/).
Use @user_passes_test or mixins for admin-only pages.
Why: Restricts access; enables navigation.
Validate: Non-logged-in users redirected; admins access admin pages.
Phase 3: Security and Web Services (30% marks)
Add protections and the REST API.

Implement remaining security (Security Layer, 14% marks) (Effort: 1 hour)

HTTPS: Configure for deployment (Django settings handle most protections: CSRF, XSS, SQL injection via ORM).
Clickjacking: Add X_FRAME_OPTIONS = 'DENY' in settings.
Why: Built-in Django features; minimal code needed.
Validate: Use tools like OWASP ZAP to test (or manually check headers).
Build REST service (Web Services, 10% marks) (Effort: 1-2 hours)

Use DRF: Create conversion/ endpoint in payapp/views.py (GET only).
Hardcode rates (e.g., GBP to USD: 1.3). Return JSON: {"rate": 1.3, "converted_amount": X} or 404 for invalid currencies.
Why: Required API.
Validate: Test with curl: GET /conversion/GBP/USD/100 returns correct data.
Phase 4: Testing and Deployment (5% marks)
Test and polish (Effort: 1-2 hours)

Run tests: Use pytest for views/models.
Fix any issues (e.g., currency conversion logic).
Why: Ensures everything works.
Validate: All features functional; no errors.
Deploy to AWS EC2 (Deployment, 5% marks) (Effort: 1-2 hours)

Set up EC2 instance, install dependencies, run python [manage.py](http://_vscodecontentref_/11) runserver 0.0.0.0:8000.
Enable HTTPS (use AWS load balancer or certbot).
Why: Final requirement.
Validate: Screenshots of commands and running app with URI.
