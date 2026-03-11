from flask import Flask
from flask_session import Session
from config import SECRET_KEY, DEBUG, HOST, PORT
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.vote_routes import vote_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize session
Session(app)

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

app.register_blueprint(vote_bp)

@app.errorhandler(404)
def not_found(error):
    from flask import render_template
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    from flask import render_template
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)

