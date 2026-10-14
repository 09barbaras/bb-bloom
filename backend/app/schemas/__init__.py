"""Pydantic schemas: the shapes of request and response JSON.

These play the role of strong params + serializers in Rails. Models (app/models)
describe the database; schemas describe the API. Keeping them separate means you
never accidentally expose `password_digest` or accept a `baby_id` from the body.
"""
