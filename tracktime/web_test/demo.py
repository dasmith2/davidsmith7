from djaveTest.web_demo import WebDemo

from tracktime.web_test.web_helper import WebHelper


class Demo(WebDemo):
  def run(self):
    helper = WebHelper(self)

    # self.go_fast()
    self.go_to_view('tracktime_homepage')
    self.say('Welcome to track time dot tech. Let me show you how it works.')
    self.say('First, lets sign up.')
    sign_up_button = self.driver.find_element_by_class_name('sign_up_button')

    self.move_click(sign_up_button, done_talking_click=True)

    email = 'jane@software.contractor'
    self.sign_up(email)

    self.say('First, I need to set up a project or two')
    helper.create_project('The Business Woman Hotel')
    helper.create_project('Bob\'s Science Laboratory')

    self.go_slow()

    self.go_to_view('demo_done')
    self.say('Thanks for checking out my demo!')
    self.wait_talking()
    self.driver.close()
