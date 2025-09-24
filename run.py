from app import create_app

app = create_app()

if __name__ == '__main__':
    if app.df_clustered_jobs is not None:
        app.run(debug=True, use_reloader=False)
    else:
        print("The application cannot be started due to a data loading error.")