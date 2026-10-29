#WİSHLİST


class Wishlist:
    def __init__(self,game):
        self.games = []


    def add_game(self, game):
        if game not in self.games:
            self.games.append(game)
        else:
            print(f"Game {game} already exists within wishlist")


    def remove_game(self, game):
        if game in self.games:

            self.games.remove(game)

        else:
            print(f"Game {game} does not exist within wishlist")



a = Wishlist("My_Wishlist")


a.add_game("Red Dead Redemption")


a.add_game("Lies of P")
a.remove_game("Red Dead Redemption")
print(a.games)

