UI Automation Testing
=====

# Page Object Model
The POM pattern is used in UI automation
* refer/create to an existing UI accessor in [tests/gui/page_objects](tests/testing_framework/page_objects)
* generate tests as unit tests with scenarios in [tests/gui](tests/gui) involving UI accessors

# Further Readings
## pyautogui
* https://pyautogui.readthedocs.io/en/latest/
* https://www.geeksforgeeks.org/gui-automation-using-python/
* https://towardsdatascience.com/automate-ui-testing-with-pyautogui-in-python-4a3762121973

## raw approach
* https://stackoverflow.com/questions/62328953/python-tkinter-gui-automation
 

## Get info on menus 
        x = self.app.menu_bar.entrycget(1, "label")
        print(x)
        # print(self.app.menu_bar.entrycget(1, 'label'))
        # print(self.app.menu_bar.entryconfigure(1))

## Move mouse + click
    # def _testfirefox(self):
    #     screenWidth, screenHeight = gui.size()
    #     gui.moveTo(0, screenHeight)
    #     gui.click()
    #     gui.typewrite('Firefox', interval=0.25)
    #     gui.press('enter')
    #     time.sleep(2)
    #     gui.keyDown('alt')
    #     gui.press(' ')
    #     gui.press('x')
    #     gui.keyUp('alt')
    #     gui.click(250, 22)
    #     gui.click(371, 51)
    #     gui.typewrite('https://medium.com/financeexplained')
    #     gui.press('enter')

## gherkin
* https://github.com/cucumber/gherkin-python