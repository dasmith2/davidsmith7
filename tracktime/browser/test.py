from tracktime.browser.demo import Demo


class Test(Demo):
  def run(self):
    self.go_fast()
    super().run()

  def demo_sign_up(self):
    self.go_to_view('tracktime_api_docs')
    self.find_with_text('h1', 'Welcome')
    self.go_to_view('tracktime_homepage')
    super().demo_sign_up()

  def do_stuff(self):
    super().do_stuff()
    self.find('not_done')
