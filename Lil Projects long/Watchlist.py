#Series watchlist


class Watchlist:
    def __init__(self,name):
        self.name = name
        self.watchlist = []


    def add_series(self,name):

        if self.name not in self.watchlist:

            self.watchlist.append(name)
        else:
            print("Movie/Series Already Exists Within your Watchlist")

    def remove_series(self,name):
        if self.name in self.watchlist:
            self.watchlist.remove(self.name)
        else:
            print("Choose a already existing series")

    def fav_show(self,name):




my_list = Watchlist("My_Watchlist")
my_list.add_series("How i met ur mother")
my_list.add_series("The Mentalist")
my_list.add_series("Harry Potter")


