from flask import  Flask
from node.blockchain.blockchain import Blockchain

# Create the application instance
app = Flask(__name__, template_folder="templates")

# Create a URL route in our application for "/"

# node = None

node = Blockchain()


@app.route('/transaction/new')
def new_transaction():
    global node
    if not node.submit_tx("008201KWANkjVuwUtSpH9fPKSAHa2D1aXx1bihE01KbittDnJdUPruz9EnFZ13m2wpqANsVWCB78164599d96f40a46498bc47a6fa5d5f8e9fc37b4fe73d59767f45f1de514307cf8e373f072f0de114c2e34fc99b34343aaf234f3f303a44c364cc67f6f8e479aeef5764038a8696702001260c7b6844ae5f272afdee45423255406de67fef78c581832d2a59471aa48a14c6565c3c935eb101d9cbf2c6ee3b073be6e233e890"):
        return 'bad transaction'
    return 'nice'

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)