"""
    Defines which database is used. One can choose between chroma and deeplake
"""

from database import VectorDatabase

db = VectorDatabase("./db", 'chroma')
