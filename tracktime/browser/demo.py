""" Don't put any asserts in here really. Put them in tracktime.browser.test
which inherits from this demo. """
from datetime import date, timedelta
from djaveTest.web_demo import WebDemo


class Demo(WebDemo):
  def run(self):
    self.warm_up()
    self.demo_sign_up()
    if self.create_first_project():
      self.punch_clock()
      self.what_a_productive_day()
      self.manual_time_entry()
      self.add_to_do_list()
      self.do_stuff()
      self.what_a_productive_day()
      self.report()
      self.invoice_rule()
      self.edit_invoice()
      self.send_invoice()
      self.all_invoices()
      self.all_to_dos()
      self.archive_project()
      self.settings()
      self.zoom()
      self.api()
      self.done()

  def first_view(self):
    return 'tracktime_homepage'

  def demo_sign_up(self):
    self.bobs = 'Bob’s Science Laboratory'
    self.hotel = 'The Business Woman Hotel'

    self.say("""
        This is a fully automated test and demonstration, so please excuse my
        robotic nature.""", wait=True)
    self.say_move_click('sign_up_button', """
        Welcome to track time dot tech! Let me show you how it works. First, I
        sign up.""")

    email = 'dave@davebase.tech'
    self.sign_up(email)

  def create_first_project(self):
    archived_projects_exist = self.find(
        '.archived-projects-link').is_displayed()
    unarchived_projects_exist = bool(self.finds(
        '#projects table tbody tr', raise_exception_if_not_found=False))
    if archived_projects_exist or unarchived_projects_exist:
      # Whoops, if there's an archive button, that means there's an existing
      # project, which means that the demo user wasn't destroyed after the last
      # demo.
      self.demo_user_wasnt_destroyed()
      return False

    self.say_move_click('newproject', """
        First, I need to set up a project. In fact, that's the only thing I can
        do.""")

    say = """
        If you were my client, I would put your name here. Let's start simple.
        I want to keep track of how much time I spend on this project."""
    self.lab_id = self.create_a_project(self.bobs, say, 'use_clock')
    return True

  def create_a_project(self, name, say, *checkboxes):
    """ checkboxes can be use_clock, has_to_do_list, and has_invoices. """
    self.say(say)
    self.move_type('name', name)
    for checkbox in checkboxes:
      self.move_click('input.{}'.format(checkbox))
    self.move_click('save', wait_talking=True)

    return self.find_pk(self.find_with_text('td', name))

  def punch_clock(self):
    self.say_move_click('enter_time_nav', (
        "Now that I have a project with a clock, the navigation "
        "shows new things I can do."))
    self.say_move_click('startclock_{}'.format(self.lab_id), (
        'I punch the clock on {}'.format(self.bobs)))

  def what_a_productive_day(self):
    self.say_move_click('punchout', """
        What a productive session. It's time to punch out.""")

  def manual_time_entry(self):
    yesterday_link = self.find('one_before').find_element_by_tag_name('a')
    self.say_move_click(yesterday_link, """
        But I just remembered I worked yesterday and forgot to punch
        the clock. I navigate to yesterday.""")
    self.say('Where I can manually enter time.', wait=True)
    self.say_move('project', """
        The project select remembers the last project I worked on.""")
    self.say_move_type('input.hours', '1', 'I enter my time')
    self.say_move_click('savenew', 'and click save new')

  def add_to_do_list(self):
    self.say_move_click('projects_nav', """
        This project is getting complicated. I'm going to need a to do
        list.""")
    self.say_move_click('edit', 'I edit the project')
    self.say_move_click('has_to_do_list', 'Turn on the to do list.')
    self.say_move_click('save', 'And click save.')
    self.say_move_click('enter_time_nav', 'Now when I punch the clock')
    self.move_click('startclock')

  def do_stuff(self):
    self.say("""
        I end up on the To Do list for this project. This is not
        a tool for creating elaborate dependency graphs.""")
    self.create_to_do(
        'The extranet should only show test results after the client pays')
    self.say("""
        It's meant to help maintain momentum, track how much time you spent,
        and paint a picture of what you did with your time.""")
    self.create_to_do(
        'Create a report of how many samples were processed per day')
    self.create_to_do('Streamline accessioning')
    self.say("""
        That last task was a bit vague. It\'s best to pick tasks you
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

  def create_to_do(self, text):
    self.move_type('textarea.description', text)
    self.move_click('todo', wait_talking=True)

  def report(self):
    self.say_move_click(
        'project_work_summary_nav', "Let's go take a look at the report.")
    self.say("""
        By default, the report shows how much time I spent on each project
        in the last week.""")
    self.move_mouse('from_date')
    self.wait(1)
    self.move_mouse('to_date')
    self.wait_mouse()
    self.wait_talking()
    self.say_move_click('.list-table a', """
        I can click on the project name to get a more detailed report.""")
    self.say("""
        The report shows my work sessions and the tasks I completed during
        those times.""", wait=True)

  def invoice_rule(self):
    say = (
        'Now that I\'m doing such great work for {}, it\'s time to create an '
        'invoice.').format(self.bobs)
    self.say_move_click('projects_nav', say)
    self.say_move_click('edit', 'I edit the project')
    self.say_move_click('has_invoices', 'And turn on invoices')
    self.say_move_click('save', 'This time when I click save')
    self.say_move_click('project_invoices_nav', 'An invoices tab appears.')

    self.say_move_click('button', """
        In order to create an invoice for {} I first create an invoice
        rule.""".format(self.bobs))

    self.say(
        'Whenever I see a dotted underline, I can hover and see an '
        'explanation.')
    self.move_mouse('.ProjectInvoiceRule .tooltip')
    self.wait_mouse()
    self.hover('.ProjectInvoiceRule .tooltip')
    self.wait(3)
    self.hover_off('.ProjectInvoiceRule .tooltip')
    self.move_mouse('h1')
    self.wait_talking()

    self.say_move_type('hourly_rate', '100', """
        Work sessions turn into a line item whose cost is equal to the hourly
        rate times the duration of the session.""")

    self.say_move_enter_date(
        'first_billable_day', date.today() - timedelta(days=1), """
            Every un invoiced work session on or after the first billable day
            will get pulled into the latest invoice. """)

    self.say_move_type('invoice_id_prefix', 'bsl_', """
        Every invoice gets a unique ID that starts with the invoice ID prefix.
        This is important to accountants.""")

    sent_to = '{}\n1 2nd St., 3rd floor\nMadison, WI, 45678'.format(self.bobs)
    self.say_move_type('sent_to', sent_to, """
        In the sent to field, I say who I will send these invoices to.""")

    make_payment_to = (
        'DaveBase.TECH\n1 2nd Ave., Unit 3\nNew York, NY, 12345')
    self.say_move_type('make_payment_to', make_payment_to, """
        In the make payment to field, I explain who I am and how my customers
        should pay me.""")

    self.say_move_type(
        'default_line_item_description', 'Software development', """
            The default line item description only comes into play if I have
            a work session where I didn't click done on any tasks.""")

    self.say_move_type('net_days', '30', """
        The invoice will be due net days after I send it.""")

    self.move_click('save', wait_talking=True)

  def edit_invoice(self):
    self.say_move_click(
        'createnewinvoice',
        'Now I can create an invoice for {}'.format(self.bobs))

    self.say_move(self.find_with_text('td', 'Created'), """
        If an invoice still has the created status""")
    self.say_move_click('#projectinvoices .edit', 'I can edit it.')

    self.say_move('#projectinvoice h1', """
        The invoice ID reflects the invoice ID prefix and the date the invoice
        was created.""")

    self.say_move('service_from', """
        Service from is automatically set to the date of the first
        work session in the invoice, which in our case happens to be
        yesterday.""")

    self.say_move('service_to', """
        Service to is automatically set to the date I created the invoice.""")

    self.say_move('[data-field="due"]', 'The due date')
    self.say_move('sent', 'is calculated based on when I send the invoice')
    self.say_move('#projectinvoice .net_days', 'and net days.')
    self.say_move_enter_date(
        'sent', date.today(), 'I will send my invoice today.')
    self.move_click('#projectinvoice .save')
    self.say_move('.status_with_date', 'So the due date is 30 days from now.')

    self.say_move_click(
        '#projectinvoices .edit', "Let's take a look at the line items")
    self.scroll_to_bottom()

    service_descriptions = self.finds('textarea.describe_service')
    self.say_move(service_descriptions[-1], """
        The last line item has a great description. It's the tasks I
        completed during that work session.""")

    say = """
        A few of the line items use the default line item description. I can
        put something a little more descriptive in there now."""
    self.say_move_type(
        service_descriptions[-3],
        'Met with Bob to discuss accessioning', say, clear_first=True)
    self.say_move_type(
        self.finds('input.amount')[-3], '40.00',
        'I can also give Bob a bit of a discount', clear_first=True)
    self.move_type(
        self.finds('textarea.amount_calculation')[-3], ' - discount')
    self.move_click('save-row')

    self.say_move_type(
        '.inline-create-row textarea.describe_service',
        'Reimburse for test order',
        'I can create manual line items as necessary')
    self.move_type('.inline-create-row input.amount', '7.23')
    self.move_click('.inline-create-row .savenew')
    self.scroll_to_bottom()
    self.say_move('.remove', """
        If I remove a line item that's based on a work session, the work
        session will appear in the next invoice.""")
    self.say_move('#lineitems .delete:contains(Delete)', """
        If I delete a manual line item, it disappears forever.""")

  def send_invoice(self):
    say = "I'm pretty happy with my invoice. Let me see the preview."
    self.say_move_click('#projectinvoice a.view', say)
    self.say("""
        It's up to me to deliver the invoice. I can copy this page and paste it
        in an email, or print this page out and mail it, whatever
        works.""", wait=True)
    self.go_to_view('project_invoices')
    self.say_move(self.find_with_text('td', 'Due '), """
        My invoice now has the status due, and the invoice row is colored
        yellow.""")
    self.say_move(
        '#projectinvoices .edit',
        'I can still edit the invoice in case Bob is unhappy.')
    self.say_move_click('paid', """
        But hopefully everything goes well and I can click
        paid.""")
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

    self.say_move('select[name=status]', "For instance I can find all Created")
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
    """
    self.say_move('download_csv_button',
        And now a few features for the accountants. You can download this table
        as a CSV.)
    """
    self.say_move_click('all_line_items', """
        You can also dig through the line items.""")
    self.say_move('#lineitems .from_date', 'You can filter')
    """
    self.say_move('download_csv_button', "And download line items as a CSV.")
    """

  def all_to_dos(self):
    self.say_move_click('to_dos_nav', """
        Let me point out a few more features related to tasks.""")
    self.say_move('button', """
        Ideally, I'm on the clock any time I'm thinking about a project.""")
    self.say_move_click('all_to_dos', """
        But sometimes it makes sense to dig through all the tasks.""")
    self.say_move('to_do_status', """
        For instance maybe I want to see all complete tasks""")
    self.find_with_text('option', 'Done').click()
    self.say_move_enter_date(
        'from_date', date.today() - timedelta(days=30),
        'created in the last 30 days for any project.')
    self.say_move('.inline-create-row select[name=project]', """
        If I'm punched in on a different project, but I remember something I
        need to do for {}""".format(self.bobs))
    to_do = 'When a customer calls, Front should display their name'
    self.say_move_type('.inline-create-row textarea.description', to_do, """
        I can do that here. It's best to plan your work and work your plan, but
        sometimes you end up describing what you did after you did it.""")
    self.say_move_click('did', """
        That's what this shortcut is for.""")
    self.say_move_click('not_done', """
        If I accidentally clicked done, I can undo""")
    self.say_move_type(
        '.row2 textarea.description', 'typos typos blah blah blah', """
            If I don't like the edits I'm making""")
    self.say_move_click('cancel-save-row', 'I can cancel them.')

  def archive_project(self):
    self.say_move_click('projects_nav', """
        When I'm completely done with a project and I don't want to see it any
        more""")
    self.say_move_click('.list-table button.delete', 'I can archive it.')
    self.say_move_click('.archived-projects-link', """
        When I realize I'm actually not done with a project""")
    self.say_move_click('unarchive', 'I can resurrect it.')

  def settings(self):
    self.say_move_click(
        'settings_url', "Let's take a look at settings.", quick=True)
    self.say_move('logout', 'I can log out here.')

  def zoom(self):
    self.say('In order to look good', wait=True)
    self.show_photo_say('phone.jpg', 'on a phone')
    self.wait(1)
    self.show_photo_say('tablet.jpg', 'Tablet')
    self.wait(1)
    self.show_photo_say('desktop.png', 'and desktop')
    self.wait(1)
    self.go_to_view('settings_tracktime')
    self.say_move('automatic_zoom', """
        Track time dot tech automatically zooms the content to fit your
        screen.""")
    self.say_move_click('zoomin', """
        But you can adjust the zoom to your liking.""")
    self.move_click('zoomin', quick=True)
    self.move_click('zoomin', quick=True)
    self.say_move_click('automatic', "I'll go back to automatic zoom.")

  def api(self):
    pass
