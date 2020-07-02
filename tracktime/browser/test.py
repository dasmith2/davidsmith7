from tracktime.browser.demo import Demo


class Test(Demo):
  def run(self):
    self.go_fast()

    super().run()
