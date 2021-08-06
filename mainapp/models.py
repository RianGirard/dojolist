from django.db import models
from django.db.models.fields import DateTimeField
import re
import bcrypt
from datetime import datetime
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.

class UserManager(models.Manager):
    def validate(self, form):
        errors = {}
        if len(form['name']) < 2:
            errors['name'] = "Name should have at least 2 characters"
        if len(form['alias']) < 2:
            errors['alias'] = 'alias should have at least 2 chacters'
        if not EMAIL_REGEX.match(form['email']):
            errors['email'] = "invalid email address"
        email_check = self.filter(email=form['email'])
        if email_check:
            errors['email'] = "email is already in use"
        if len(form['password']) < 8:
            errors['password'] = "Password should have length of 8 charcters"
        if form['password'] != form['confirm']:
            errors['password'] = 'Passwords do not match'
        return errors

    def validate_update(self, form):
        errors = {}
        if len(form['name']) < 2:
            errors['name'] = "Name should have at least 2 characters"
        if len(form['alias']) < 2:
            errors['alias'] = "Alias should have at least 2 chacters"
        return errors

    def register(self, form):
        pw = bcrypt.hashpw(form['password'].encode(),
            bcrypt.gensalt()).decode()
        return self.create(name=form['name'], alias=form['alias'],
            email=form['email'], password=pw)

    def authenticate(self, email, password):
        users = self.filter(email=email)
        if not users:
            return False
        user = users[0]
        return bcrypt.checkpw(password.encode(), user.password.encode())


class User(models.Model):
    name = models.CharField(max_length=45)
    alias = models.CharField(max_length=45)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=45)
    community = models.CharField(max_length=45, default='seattle')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models, DateTimeField(auto_now=True)
    objects = UserManager()

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=200)
    subcategory = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=5)
    community = models.CharField(max_length=200)
    date = models.DateField(default=datetime.now) 
    publisher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} by: {self.publisher.name}'
# Create your models here.
