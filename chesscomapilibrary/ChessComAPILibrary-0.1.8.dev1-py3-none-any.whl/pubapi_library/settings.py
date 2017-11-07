"""Settings file."""
from tortilla import wrap

# Chess.com APIs
PUBLIC_API = wrap("https://api.chess.com/pub", delay=3.0)
REQUEST_HEADERS = {'User-Agent': 'ChessComAPILibrary/1.0 '
                                 '(Author: Walid Mujahid, '
                                 'Email: walid.mujahid.dev@gmail.com, '
                                 'Chess.com username: walidmujahid.)'}
