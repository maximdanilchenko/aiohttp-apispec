from aiohttp import web


from example.app import create_app


if __name__ == "__main__":
    web_app = create_app()
    web.run_app(web_app)

