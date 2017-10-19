
def main():
    from vidjon_messenger_api.db import db
    from vidjon_messenger_api.app import app
    db.init_app(app)
    app.run(port=5000, debug=True)

if __name__ == '__main__':
    main()