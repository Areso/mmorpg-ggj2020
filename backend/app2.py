open_sessions = []
open_sessions.append(["sad123xc123x", "player1", 0, ""])
open_sessions.append(["Q5x1246swWl2", "player2", 0, ""])
open_sessions.append(["3CAD246sTT44", "player3", 0, ""])

def get_login(token):
    for each_session in open_sessions:
        session_token = each_session[0]
        if session_token == token:
            session_login = each_session[1]
            return print(session_login)
            break

get_login("Q5x1246swWl2")
