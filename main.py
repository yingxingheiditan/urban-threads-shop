from website import create_app

app = create_app()

if __name__ == '__main__':
    # can specify host address and port if you want
    # app.run(debug=True, host='192.168.0.1', port=8080)
    app.run(debug=True)