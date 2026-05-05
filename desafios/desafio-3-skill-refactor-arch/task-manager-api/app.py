from src.app import create_app
from src.config.settings import Config

app = create_app(Config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)
