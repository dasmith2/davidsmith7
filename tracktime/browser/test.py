from tracktime.browser.demo import Demo


class Test(Demo):
  def run(self):
    self.go_fast()
    super().run()

  def do_stuff(self):
    super().do_stuff()
    self.find('not_done')
