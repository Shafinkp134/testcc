from flask import render_template, session, redirect, url_for, make_response, abort, request, jsonify
from app_init import app
from models import db, User, Admin, SupportChat
from datetime import datetime
import logging

def is_admin():
    if 'user' not in session or 'user_email' not in session['user']:
        return False
    admin = Admin.query.filter_by(email=session['user']['user_email']).first()
    return admin is not None

# Add initial admin
with app.app_context():
    initial_admin_email = "Shaafinkp151@gmail.com"
    existing_admin = Admin.query.filter_by(email=initial_admin_email).first()
    if not existing_admin:
        new_admin = Admin(email=initial_admin_email)
        db.session.add(new_admin)
        db.session.commit()
        logging.info(f"Added initial admin: {initial_admin_email}")

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500
    
@app.route("/")
def landing_route():
    return render_template("landing.html")

@app.route("/home")
def home_route():
    # Determine the current day for a new user
    current_day = 1  # Default to first day for new users
    return render_template("home.html", current_day=current_day)

@app.route("/support")
def support_route():
    return render_template("support.html")

@app.route("/admin/dashboard")
def admin_dashboard_route():
    if not is_admin():
        abort(403)
    
    user_count = User.query.count()
    chat_count = SupportChat.query.count()
    admin_count = Admin.query.count()
    
    return render_template("admin/index.html", 
                          user_count=user_count,
                          chat_count=chat_count,
                          admin_count=admin_count)

@app.route("/admin/users")
def admin_users_route():
    if not is_admin():
        abort(403)
    
    users = User.query.all()
    return render_template("admin/users.html", users=users)

@app.route("/admin/users/<int:user_id>", methods=['DELETE'])
def admin_delete_user(user_id):
    if not is_admin():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route("/admin/manage")
def admin_manage_route():
    if not is_admin():
        abort(403)
    
    admins = Admin.query.all()
    return render_template("admin/manage.html", admins=admins)

@app.route("/admin/manage", methods=['POST'])
def admin_add_admin():
    if not is_admin():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'success': False, 'error': 'Email is required'}), 400
    
    if Admin.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Admin already exists'}), 400
    
    new_admin = Admin(email=email)
    db.session.add(new_admin)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route("/admin/manage/<int:admin_id>", methods=['DELETE'])
@app.route("/admin/chat")
def admin_chat_route():
    if not is_admin():
        abort(403)
    
    chats = SupportChat.query.order_by(SupportChat.timestamp.desc()).all()
    users = User.query.all()
    
    return render_template("admin_chat.html", chats=chats, users=users)

@app.route("/admin/chat/respond", methods=['POST'])
def admin_chat_respond():
    if not is_admin():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    user_email = data.get('user_email')
    message = data.get('message')
    
    if not user_email or not message:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    chat = SupportChat.query.filter_by(user_id=user.id).order_by(SupportChat.timestamp.desc()).first()
    if chat:
        chat.admin_response = message
        chat.response_timestamp = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'No chat found for user'}), 404

@app.route("/logout", methods=['GET'])
def logout_route():
    session.clear()
    return redirect(url_for('landing_route'))