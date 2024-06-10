from app import create_app
from utils import scrape_image

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)