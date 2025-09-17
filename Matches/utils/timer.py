from threading import Thread
import threading
from datetime import datetime, timedelta
import time

def start_disconnection_timer(match_id: int, player_id: int, timeout_seconds: int = 10):
    """
    Start a background timer for player disconnection
    """
    def timer_callback():
        time.sleep(timeout_seconds)
        
        from Matches.models import Matches
        try:
            match = Matches.objects.get(id=match_id)
            if match.status != "completed":
                player_still_disconnected = True if match.player1.player_id == player_id and match.player1_disconnected else True if match.player2.player_id == player_id and match.player2_disconnected else False
                if player_still_disconnected:
                    winner = match.player2 if match.player1.player_id == player_id else match.player1
                    match.winner = winner
                    match.status = "completed"
                    match.save()
        except Matches.DoesNotExist:
            pass
    
    timer_thread = threading.Thread(target=timer_callback)
    timer_thread.daemon = True
    timer_thread.start()