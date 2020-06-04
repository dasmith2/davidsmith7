from djaveTest.web_demo import WebDemo


class Demo(WebDemo):
  def run(self):
    self.go_to_view('enter_time')
    self.login('dave@dave.dave')
    self.say('Welcome to the time entry page')
