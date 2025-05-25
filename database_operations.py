from models import db, User

def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return {
            'id': user.id,
            'email': user.email,
            'profile_picture': user.profile_picture
        }
    return None