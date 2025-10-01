from project import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True 適用於開發。對於生產環境，請將其設置為 False。
    # host='0.0.0.0' 使其可在您的本地網路上訪問。
    app.run(debug=True, host='0.0.0.0')