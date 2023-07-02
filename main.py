from fastapi import FastAPI, Depends, Body, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token
from fastapi.security import HTTPBearer
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel

app = FastAPI()
app.title = "My First API"

Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super.__call__(request)


class User(BaseModel):
    user: str
    password: str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(max_length=15)
    overview: str
    year: int = Field(le = 2023)
    rating: float = Field(ge = 1,le = 10.0)
    category: str  

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Titulo de la pelicula",
                "overview": "descripcion de la pelicula",
                "year": 2023,
                "rating": 9.8,
                "category": "genero"
            }
        }

movies = [
    {
        'id': 1,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': 2009 ,
        'rating': 7.8,
        'category': 'Acción'    
    },
    {
        'id': 2,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': 2009,
        'rating': 7.8,
        'category': 'Acción'    
    } 
]


#Moldulo de autenticacion
@app.get("/login", tags=["Auth"])
def login(user: User):
    return user


#GET root
@app.get("/", tags=["root"])
def message():
    return HTMLResponse("<h1>Hola Gabriela tqm <3</h1>")


#GET todas las peliculas
@app.get("/movies", tags=["movies"])
def get_movies():
    db = Session()
    result = db.query(MovieModel).all()
    return JSONResponse(content = jsonable_encoder(result))


#GET pelicula por id
@app.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: int):
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not result:
        return JSONResponse(content = {'message': 'id not found'}, status_code=404)
    return JSONResponse(content = jsonable_encoder(result), status_code=201)


#GET pelicula por categoria y año
@app.get("/movies/", tags=["movies"], response_model= List[Movie], dependencies=[Depends(JWTBearer())])
def get_movie_by_category(category: str, year: int):
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.category == category, MovieModel.year == year).all()
    if not result:
        return JSONResponse(content = {'message': 'movie not found'}, status_code=404)
    return JSONResponse(content = jsonable_encoder(result), status_code=201)
    


#POST crear nueva pelicula
@app.post("/movies", tags=["movies"], response_model= List[Movie], status_code=201)
def add_movie(movie: Movie):
    db = Session()
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    db.commit()
    movies.append(movie.dict())
    return JSONResponse(content = movies)


#PUT actualizar pelicula
@app.put("/movies/{movie_id}", tags=["movies"])
def upddate_movie(movie_id:int, movie: Movie):
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not result:
        return JSONResponse(content = {'message': 'id not found'}, status_code=404)
    result.title = movie.title
    result.overview = movie.overview
    result.year = movie.year
    result.rating = movie.rating
    result.category = movie.category
    db.commit()
    return JSONResponse(content = {"message": "registro modificado"}, status_code=201)
        

#DELETE eliminar pelicula
@app.delete("/movies/{movie_id}", tags=["movies"])
def delete_movie(movie_id: int):
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not result:
        return JSONResponse(content = {'message': 'id not found'}, status_code=404)
    db.delete(result)
    db.commit()
    return JSONResponse(content = {'message' : f'id: {movie_id} borrado con exito'}, status_code=201)
    