import sublime
import sublime_plugin
import re

# TODO: TAB or space on a empty bullet will indent it
# TODO: Backspace on a indented empty bullet will unindent it
# TODO: Backspace on a unindented empty bullet will delete it
# TODO: Better multi line pasting behaviour (esp the bug that if you paste a 2 lines content, a * will be added to the end of the pasting )
#       Just check whether the line is a empty line before inserting

class BulletIndent(sublime_plugin.TextCommand):
  def run(self, edit):
    self.view.window().run_command("indent")

class BulletUnindent(sublime_plugin.TextCommand):
  def run(self, edit):
    self.view.window().run_command("unindent")

class Bullet(sublime_plugin.EventListener):
  Modifying = False
  is_markdown = False
  last_line = 0
  last_pos = 0
  selectors = []

  def __init__(self):
    s = sublime.load_settings("Bullet.sublime-settings")
    Bullet.selectors = s.get("markdown_bullet_selectors", [])

  def on_activated(self, view):
    for x in range(len(Bullet.selectors)):
      if (view.score_selector(0,Bullet.selectors[x]) > 0):
        Bullet.is_markdown = True
        Bullet.update_row(self, view)
        return
      else:
        Bullet.is_markdown = False
  
  def on_selection_modified(self, view):
    if (Bullet.is_markdown):
      Bullet.update_row(self, view)
    
  def update_row(self, view):
    loc = view.sel()[0]
    Bullet.last_pos = loc.begin()
    row, col = view.rowcol(Bullet.last_pos)
    Bullet.last_line = row

  def on_modified(self, view):
    if Bullet.Modifying == False:
      Bullet.Modifying = True
      if Bullet.is_markdown == True:
        loc = view.sel()[0]
        row, col = view.rowcol(loc.begin())
        point_last_row = view.text_point(row-1,0)

        #if (row - Bullet.last_line == 0):
        #  current_line_region = view.line(loc.begin())
        #  current_line = view.substr(current_line_region)
        #  if current_line != "":
        #    match_pattern = re.search("^( *|\t*)(\*|\-|\>|\+|[0-9]+\.)(.*)$",current_line)
        #    if match_pattern != None:
        #      if match_pattern.group(3) == "":
        #        if Bullet.last_pos >= loc.begin():
        #          if match_pattern.group(1) != "":
        #            edit = view.begin_edit()
        #            view.insert(edit,current_line_region.end()," ")
        #            view.erase(edit,sublime.Region(current_line_region.begin(),current_line_region.begin()+1))
        #            view.end_edit(edit)
        #          else:
        #            edit = view.begin_edit()
        #            view.erase(edit,current_line_region)
        #            view.end_edit(edit)
        #      else:
        #        match_space = re.search("^(( )( )+|\t)$", match_pattern.group(3))
        #        if match_space != None:
        #          if match_pattern.group(1) == None:
        #            indented_part = ""
        #          else:
        #            indented_part = match_pattern.group(1)
        #          insertion_location = current_line_region.begin()
        #          edit = view.begin_edit()
        #          view.erase(edit,current_line_region)
        #          view.insert(edit, insertion_location , "\t" + indented_part + match_pattern.group(2) + " ")
        #          view.end_edit(edit)
        #elif (row - Bullet.last_line == 1):
        if (row - Bullet.last_line == 1):
          previous_line = view.substr(view.line(Bullet.last_pos))
          if row != 0 and previous_line != "":
            match_pattern = re.search("^( *|\t*)(\*|\-|\>|\+|[0-9]+\.)(.*)",previous_line)
            if match_pattern != None:
              if match_pattern.group(3) == " " or match_pattern.group(3) == "":
                reg_remove = view.find("(\*|\-|\>|\+|[0-9]+\.)(.*)",point_last_row-1)
                edit = view.begin_edit()
                view.erase(edit,reg_remove)
                view.end_edit(edit)
              else:
                if match_pattern.group(2) == "*":
                  insertion = "* "
                elif match_pattern.group(2) == "-":
                  insertion = "- "
                elif match_pattern.group(2) == ">":
                  insertion = "> "
                elif match_pattern.group(2) == "+":
                  insertion = "+ "
                else:
                  match_number = re.search("[0-9]+",match_pattern.group(2))
                  if match_number != None:
                    last_number = int(match_number.group(0))
                    insertion = str(last_number+1) + ". "
                  else:
                    insertion = ""
                edit = view.begin_edit()
                view.insert(edit, loc.end(), insertion)
                view.end_edit(edit)

      
    Bullet.update_row(self, view)
    Bullet.Modifying = False