from models import db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class UserService:
    def get_user_by_id(self, user_id):
        return User.query.get_or_404(user_id)

    def get_user_tags(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            return {tag for tag in user.tags} | {
                tag for fav in user.favorites for tag in fav.tags
            }
        return set()

    def update_user(self, user, data):
        user.username = data["username"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data["email"]
        user.img_url = data["img_url"]
        user.profile_img_url = data["profile_img_url"]

        if data.get("password"):
            user.password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

        db.session.commit()
        
    def delete_user(self, user_id):
        db.session.delete(user_id)
        db.session.commit()
        
