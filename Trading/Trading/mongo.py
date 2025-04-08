from mongoengine import connect, disconnect

# Disconnect any existing connections before connecting
# disconnect(alias='default')

# Now, connect to MongoDB
connect(
    db='trade_today',
    host='localhost',
    port=27017,
    # alias='default'  # Ensure this alias is used for the connection
)
