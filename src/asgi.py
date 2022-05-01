import uvicorn

if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        workers=4,
        reload=True,
    )