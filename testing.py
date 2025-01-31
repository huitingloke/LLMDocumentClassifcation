import datetime

new_metadata = {
    "title": "Test",
    "author": "Test",
    "date": "Test",
    "content": "Test"
}
new_metadata += {
    "date": datetime.datetime.now() # Converts to epoch time
}