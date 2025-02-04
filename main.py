from fastapi import FastAPI
# From absolute path
# import models
# from database import engine


# From relative path
from .models import Base
from .database import engine
from .routers import auth, todos, admin, user

app = FastAPI()

# For absolute path
# models.Base.metadata.create_all(bind=engine)

# For relative path
Base.metadata.create_all(bind=engine)

# Just to check everything is OK for testing
# Typically it should be checked
@app.get("/healthy")
def health_check():
    return { "status": "Healthy" }


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)
