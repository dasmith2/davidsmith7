from datetime import date, timedelta
from djaveTest.web_demo import WebDemo

from tracktime.browser.web_helper import WebHelper


class Demo(WebDemo):
  def run(self):
    self.go_fast()

    self.warm_up()
    self.demo_sign_up()
    self.create_projects()
    self.punch_clock()
    self.do_stuff()
    self.manual_time_entry()
    self.report()
    self.invoice_rule()
    self.edit_invoice()
    self.send_invoice()
    self.all_invoices()
    self.all_tasks()
    self.archive_project()
    self.settings()
    self.api()

    self.done()

  def first_view(self):
    return 'tracktime_homepage'

  def demo_sign_up(self):
    self.helper = WebHelper(self)

    self.bobs = 'Bob’s Science Laboratory'
    self.hotel = 'The Business Woman Hotel'

    self.say_move_click('sign_up_button', """
        Welcome to track time dot tech. Let me show you how it works. First,
        lets sign up.""")

    email = 'dave@software.company'
    self.sign_up(email)

  def create_projects(self):
    if self.finds('archive', raise_exception_if_not_found=False):
      # Whoops, if there's an archive button, that means there's an existing
      # project, which means that the demo user wasn't destroyed after the last
      # demo.
      return self.demo_user_wasnt_destroyed()
    self.say("""
        First, I need to set up a project or two. If you were my client, I
        would put your company's name here.""")

    self.hotel_id = self.helper.create_project(self.hotel)
    self.lab_id = self.helper.create_project(self.bobs)

  def punch_clock(self):
    self.say_move_click('entertime_nav', """
        Now that I'm done setting up a few projects, let's get to work. I
        navigate to enter time.""")
    self.say_move_click('starttheclock_{}'.format(self.lab_id), """
        I'm going to do a few tasks for {}, so I start the
        clock.""".format(self.bobs))

  def do_stuff(self):
    self.say("""
        Now that I'm on the clock, it's time to decide what to do. This is not
        a tool for creating elaborate dependency graphs.""")
    self.helper.create_to_do(
        'The extranet should only show test results after the client pays')
    self.say("""
        It's meant to help maintain momentum, track how much time you spend,
        and paint a picture of what you do.""")
    self.helper.create_to_do(
        'Create a report of how many samples were processed per day')
    self.helper.create_to_do('Streamline accessioning')
    self.say("""
        That last task was a bit vague. It\'s best to pick tasks that I
        can reasonably accomplish in a single session, because that's going to
        create beautiful invoices. Notice that the row I\'m editing turned
        yellow, and the buttons changed.""")
    elt = self.find_with_value('description', 'Streamline accessioning')
    self.move_type(
        elt,
        'When you scan a sample barcode, automatically tab to the next field',
        clear_first=True)
    self.move_click('save-row', wait_talking=True)
    self.say_move_click('done', """
        When I complete a task, I click done, and the row turns green.""")
    self.say("""
        Keeping green rows on the page is a real Sisyphean endeavor because
        green rows only stick around for 24 hours.""")
    self.wait(2)
    self.move_click('done')
    self.wait(2)
    self.say_move_click('punch_out_on_to_do', """
        What a productive day. It's time to punch out.""")
    self.at_least_some_time()

  def at_least_some_time(self):
    """ Make sure all the Project Work Sessions on the "Enter time" page have
    at least 0.01 hours, which is important because when you go fast through
    do_stuff the work session has duration 0 which means nothing appears in the
    report. """
    for elt in self.finds('hours'):
      if elt.text.find('0.0 ') == 0:
        pk = self.find_pk(elt)
        self.helper.set_to_do_hours(pk, 0.01)

  def manual_time_entry(self):
    yesterday_link = self.find('one_before').find_element_by_tag_name('a')
    self.say("""
        Once I punch out, I land back on the Enter Time page, where I can punch
        back in.""", wait=True)
    self.say_move_click(yesterday_link, """
        But I just remembered I worked yesterday and forgot to punch
        the clock. I navigate to yesterday.""")
    self.say('Where I can manually enter time.', wait=True)
    self.say_move('project', """
        The project select remembers the last project I worked on.""")
    self.say_move_type('hours', '0.5', 'I enter my time')
    self.say_move_click('savenew', 'and click save new')
    self.say("I also worked on {} yesterday.".format(self.hotel))
    self.move_mouse('project')  # project select box
    self.wait_mouse()
    self.find_with_value('option', str(self.hotel_id)).click()
    self.move_type('hours', '2')
    self.move_click('savenew', wait_talking=True)

  def report(self):
    self.say_move_click('report_nav', "Let's go take a look at the report.")
    self.say("""
        By default, the report shows how much time I spent on each project
        in the last week.""")
    self.move_mouse('from_date')
    self.wait(1)
    self.move_mouse('to_date')
    self.wait_mouse()
    self.wait_talking()
    self.say_move_click('details_{}'.format(self.lab_id), """
        I can click on the hours to get a more detailed report.""")
    self.say("""
        The report shows my work sessions and the tasks I completed during
        those times.""", wait=True)

  def invoice_rule(self):
    self.say_move_click(
        'invoices_nav', "Now let's go take a look at invoices.")

    self.say_move_click('button', """
        In order to create an invoice for {} I first create an invoice
        rule.""".format(self.bobs))

    self.say(
        'Whenever I see a dotted underline, I can hover and see an '
        'explanation.')
    self.move_mouse('tooltip')
    self.wait_mouse()
    self.hover('tooltip')
    self.wait(3)
    self.hover_off('tooltip')
    self.move_mouse('h1')
    self.wait_talking()

    self.move_mouse('project')
    self.wait_mouse()
    self.find_with_value('option', str(self.lab_id)).click()

    self.say_move_type('hourly_rate', '100', """
        Work sessions turn into a line item whose cost is equal to the hourly
        rate times the duration of the session.""")

    self.say_move_enter_date(
        'first_billable_day', date.today() - timedelta(days=1), """
            Every un invoiced work session on or after the first billable day
            will get pulled into the latest invoice. """)

    self.say_move_type('invoice_id_prefix', 'bsl_', """
        Every invoice gets a unique ID that starts with the unique ID prefix.
        This is important to accountants.""")

    sent_to = '{}\n1 2nd St., 3rd floor\nMadison, WI, 45678'.format(self.bobs)
    self.say_move_type('sent_to', sent_to, """
        In the sent to field, I say who I will send these invoices to.""")

    make_payment_to = (
        'Dave\'s Software Company\n9 10th Ave., Unit 11\nNew York, NY, 12131')
    self.say_move_type('make_payment_to', make_payment_to, """
        In the make payment to field, I explain who I am and how my customers
        should pay me.""")

    self.say_move_type(
        'default_line_item_description', 'Software development', """
            The default line item description only comes into play if I have
            a work session where I didn't click done on any tasks.""")

    self.say_move_type('net_days', '30', """
        When I create an invoice, I will pick the day I intend to send out the
        invoice. The due date will be set net days from then.""")

    self.move_click('save', wait_talking=True)

  def edit_invoice(self):
    self.say_move_click(
        'createnewinvoice',
        'Now I can create an invoice for {}'.format(self.bobs))

    self.say_move(self.find_with_text('td', 'Created'), """
        If an invoice still has the created status""")
    self.say_move_click('edit', 'I can edit it.')

    self.say_move('h1', """
        The invoice ID reflects the invoice ID prefix and the date the invoice
        was created.""")

    self.say_move('service_from', """
        Service from is automatically set to the date of the first
        work session in the invoice, which in our case happens to be
        yesterday.""")

    self.say_move('service_to', """
        Service to is automatically set to the date I created the invoice.""")

    self.say_move(self.find_with_text('div', 'Due'), 'The due date')
    self.say_move('sent', 'is calculated based on when I send the invoice')
    self.say_move('net_days', 'and net days.')
    self.say_move_enter_date(
        'sent', date.today(), 'I will send my invoice today.')
    self.move_click('save')

    self.say("Let's take a look at the line items")
    self.scroll_to_bottom()

    self.say_move('describe_service', """
        The first line item has a great description. It's the tasks I
        completed during that work session.""")

    say = """
        The second line item uses the default line item description. I can put
        something a little more descriptive in there now."""
    self.say_move_type(
        self.finds('describe_service')[1],
        'Met with Bob to discuss accessioning', say, clear_first=True)
    self.say_move_type(
        self.finds('amount')[1], '40.00',
        'I can also give Bob a bit of a discount', clear_first=True)
    self.move_type(self.finds('amount_calculation')[1], ' - discount')
    self.say_move_click('save-row', 'Remember that a yellow row is unsaved')

    self.say_move_type(
        'new_description', 'Reimburse for test order',
        'I can create manual line items as necessary')
    self.move_type('new_amount', '7.23')
    self.say_move_click('newmanuallineitem', "Don't forget to save")
    self.scroll_to_bottom()
    self.say_move('remove', """
        If I remove a line item that's based on a work session, the work
        session will appear in the next invoice.""")
    self.say_move('delete_line_item', """
        If I delete a manual line item, it disappears forever.""")

  def send_invoice(self):
    self.say_move_click('saveandpreview', """
        I'm pretty happy with my invoice. Let me see the preview.""")
    self.say("""
        It's up to me to deliver the invoice. I can copy this page and paste it
        in an email, or print this page out and mail it, whatever
        works.""", wait=True)
    self.go_to_view('project_invoices')
    self.say_move(self.find_with_text('td', 'Due '), """
        My invoice now has the status due, and the invoice row is colored
        yellow.""")
    self.say_move(
        'edit', 'I can still edit the invoice in case Bob is unhappy.')
    self.say_move_click('markpaid', """
        But hopefully everything goes well and I can click
        mark paid.""")
    self.say_move(self.find_with_text('td', 'Paid'), """
        My invoice now has the status paid, the invoice row is colored green,
        and I can no longer edit.""")
    self.say_move_click('view', """
        If I view the invoice now, it will show payment.""")
    self.wait(2)
    self.go_to_view('project_invoices')

  def all_invoices(self):
    self.say_move_click('all_invoices', """
        Green invoices linger on this page for two days, but I can find any
        invoice at any time here.""")

    import pdb
    pdb.set_trace()

    self.say_move('status', "For instance I can find all Created")
    self.find_with_text('option', 'Created').click()
    self.say('Due', wait=True)
    self.find_with_text('option', 'Due').click()
    self.say('Late', wait=True)
    self.find_with_text('option', 'Late').click()
    self.say('or paid invoices', wait=True)
    self.find_with_text('option', 'Paid').click()

    self.say_move('project', "For {}".format(self.bobs))
    self.find_with_text('option', 'Bob').click()

    self.say_move_enter_date(
        'from_date', date.today() - timedelta(days=365), 'In the last year')
    self.move_click('report')
    self.say_move('download_csv_button', """
        And now a few features for the accountants. You can download this table
        as a CSV.""")
    self.say_move_click('all_line_items', """
        You can also dig through the line items.""")
    self.say_move('from_date', 'You can filter')
    self.say_move('download_csv_button', "And download line items as a CSV.")

  def all_tasks(self):
    self.say_move_click('todo_nav', """
        Let me point out a few more features related to tasks.""")
    self.say_move('starttheclock', """
        Ideally, I'm on the clock any time I'm thinking about a project.""")
    self.say_move_click('all_tasks', """
        But sometimes it makes sense to dig through all the tasks.""")
    self.say_move('to_do_status', """
        For instance maybe I want to see all complete tasks""")
    self.find_with_text('option', 'Done').click()
    self.say_move_click('report', 'created in the last month for any project.')
    self.say_move(self.finds('project')[1], """
        If I'm punched in on {}, but I remember something I need to do for
        {}""".format(self.bobs, self.hotel))
    self.finds_with_text('option', self.hotel)[1].click()
    to_do = (
        'When a guest changes rooms, automatically schedule an immediate '
        'cleaning in the old unit')
    self.say_move_type('new_description', to_do, """
        I can do that here. It's best to plan your work and work your plan, but
        sometimes I end up describing what I did after I did it.""")
    self.say_move_click('did', """
        That's what this shortcut is for.""")
    self.say_move_click('not_done', """
        If I accidentally clicked done, I can undo""")
    self.say_move_type(
        'description', 'typos typos blah blah blah', """
            If I don't like the edits I'm making""")
    self.say_move_click('cancel-save-row', 'I can cancel them.')

  def archive_project(self):
    self.say_move_click('projects_nav', """
        When I'm completely done with a project and I don't want to see it any
        more""")
    self.say_move_click('archive', 'I can archive it.')
    self.say_move_click('archived_projects', """
        When I realize I'm actually not done with a project""")
    self.say_move_click('unarchive', 'I can resurrect it.')

  def settings(self):
    self.say_move_click('settings_url', "Let's take a look at settings.")
    self.say_move('logout', 'I can log out here.')

  def api(self):
    self.say_move_type('username', 'daves_data', """
        But much more interesting is the API. Here you can create an API
        key.""")
    self.say_move_type('new_webhook_url', 'https://your.website', """
        If you specify a webhook url, Track Time dot tech will send data to
        your computers whenever your data changes.""")
    self.move_click('create')
    self.say_move_click('api_docs', """
        Now that I have an API key username and password, let me explain the
        significance.""")
    self.say("""
        The API gives you total power over your own data. You can program your
        own computers to read, write, or delete any important object according
        to your own logic.""", wait=True)
    self.say_scroll(self.find_with_text('h1', 'ManualLineItem'), """
        For example you could dynamically add line items to your invoices.""")
    self.say_scroll(self.find_with_text('h1', 'ProjectInvoice'), """
        You could write an automation that bugs your customers for overdue
        invoices.""")
    self.say_scroll(self.find_with_text('h1', 'Welcome'), """
        You're limited only by your imagination and the competence of
        your engineers.""")

  def done(self):
    from selenium.common.exceptions import WebDriverException
    try:
      # I often save a file and then immediately hit continue on a trace
      # session, which then often flies immediately to this page, which then
      # fails to load because ./manage.py runserver is reloading.
      self.go_to_view('demo_done')
    except WebDriverException:
      self.sleep(1)
      self.go_to_view('demo_done')
    self.say("""
        I built track time dot tech so everyone would know I'm ready to take on
        my own clients. I am open to charging per hour, or per
        unit.""", wait=True)
    self.say("""
        I'm particularly interested to build automations and workflows for
        laboratories and hotels. Thanks for checking out my demo!""")
    self.wait_talking()
    self.driver.close()

  def demo_user_wasnt_destroyed(self):
    self.go_to_view('demo_done')
    self.go_slow()
    self.say("""
        It appears that the demo user wasn't successfully destroyed after the
        last demo, so I destroyed them now. I'm afraid you will have to
        restart the demo.""")
    self.wait_talking()
    self.driver.close()
