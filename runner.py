"""Flask code to expose this as API"""

from app import create_app
from config import Config

application = create_app()

if __name__ == '__main__':
  application.run(port=Config.FLASK_PORT)