##### startup script #####

#!/opt/bin/lv_micropython -i

import lvgl as lv
import fs_driver


##### main script #####


class CALC_APP(object):

    def __init__(self):
        self.operator = [None,None]
        self.result = None
        self.operation = None


    def setup(self, screen):
        self.screen = screen
        style_ta = lv.style_t()
        style_ta.init()
        style_ta.set_border_width(5)
        style_ta.set_border_color(lv.color_black())
        self.ta = lv.textarea(screen)
        self.ta.set_one_line(True)
        self.ta.set_size(100,60)
        self.ta.add_style(style_ta,0)
        self.ta.align(lv.ALIGN.TOP_RIGHT, 0, 0)
        self.ta.set_align(lv.TEXT_ALIGN.RIGHT)

        self.la = lv.label(screen)
        self.la.set_text("")
        self.la.set_size(20,20)
        self.la.align_to(self.ta, lv.ALIGN.OUT_LEFT_MID, 5, 15)
        self.ta.add_state(lv.STATE.DISABLED)

        head = lv.label(screen)
        style = lv.style_t()
        style.init()

        fs_drv = lv.fs_drv_t()
        fs_driver.fs_register(fs_drv, 'S')
        medula26 = lv.font_load("S:medula26.fnt")
        style.set_text_font(medula26)
        style.set_border_width(2)
        style.set_radius(10)
        style.set_border_color(lv.palette_main(lv.PALETTE.GREY))
        style.set_opa(lv.OPA._30)
        head.add_style(style,0)

        head.set_text(" LVGL MPY \n   CALCULATOR ")
        head.align(lv.ALIGN.TOP_LEFT, 0, 0)

        btnm_map = [ "%", "CE", "C", "/", "\n",
                    "1", "2", "3", lv.SYMBOL.CLOSE, "\n",
                    "4", "5", "6", lv.SYMBOL.PLUS, "\n",
                    "7", "8", "9",  lv.SYMBOL.MINUS, "\n",          
                    "0", ".", lv.SYMBOL.BACKSPACE, lv.SYMBOL.NEW_LINE, ""]

        style_bg = lv.style_t()
        style_bg.init()
        style_bg.set_pad_all(1)
        style_bg.set_pad_gap(2)
        style_bg.set_border_width(1)

        self.btnm = lv.btnmatrix(screen)
        self.btnm.set_size(240, 160)
        self.btnm.add_style(style_bg, 0)
        self.btnm.align(lv.ALIGN.BOTTOM_MID, 0, 8)
        self.btnm.add_event(lambda e: self.btnm_event_handler(e, self.ta), lv.EVENT.CLICKED, None)
        self.btnm.clear_flag(lv.obj.FLAG.CLICK_FOCUSABLE)    # To keep the text area focused on button clicks
        self.btnm.set_map(btnm_map)

        
    def get_operator(self, num=1): #get  self.operator
        try:
            if num == 1:
                text = self.ta.get_text()
                self.operator[num-1] = float(text)
                self.ta.set_text( text + "\n")
                return True
            else:
                text = self.ta.get_text().split("\n")
                self.operator[num-1] = float(text[-1]) 
                return True
        except:
            print("Error Getting Operator")

    def check_op(self, op = "="):
        if self.operation == op:
            return True
        else:
            self.operation = op
            self.la.set_text(self.operation)
            return False

    def end_calc(self, symbol = "="): #finish calculations and update UI
         self.operator[0] = self.result
         self.operator[1] = None
         self.ta.set_text(str(self.result) + "\n")
         self.operation = symbol
         self.la.set_text(self.operation)


    def btnm_event_handler(self, e, ta): #main operation
        obj = e.get_target_obj()
        txt = obj.get_btn_text(obj.get_selected_btn())

        if txt == lv.SYMBOL.BACKSPACE:
            self.ta.del_char()

        elif txt == "C":
            self.ta.set_text("")
            self.operator = [None,None]
            self.operation = None
            self.la.set_text("=")

        elif txt == "CE":
            if  self.operator[0] != None:
                self.operation = None
                self.la.set_text("=")
                self.ta.set_text(str(self.operator[0]))
                self.operator[0] = None
                self.la.set_text("=")


        elif txt == lv.SYMBOL.NEW_LINE: #equal
            if  self.operator[0] != None:
                if  self.operator[1] == None:
                    text = self.ta.get_text().split("\n")
                    if len(text) > 1 and text[-1] != "":
                        self.get_operator(2)
                    else:
                         self.operator[1] =  self.operator[0]
                if self.operation == None:
                     self.operator = [None,None]
                else:
                    if  self.operator[1] != None:
                        print(" {} {} {}".format(self.operator[0], self.operation,  self.operator[1]))
                        if self.operation == "/":
                            if  self.operator[1] != 0:
                                self.result = float(self.operator[0] /  self.operator[1])
                            else:
                                self.result = "Error"
                        elif self.operation ==  lv.SYMBOL.CLOSE:
                            self.result = float(self.operator[0] *  self.operator[1])
                        elif self.operation == lv.SYMBOL.PLUS:
                            self.result = float(self.operator[0] +  self.operator[1])
                        elif self.operation == lv.SYMBOL.MINUS:
                            self.result = float(self.operator[0] -   self.operator[1])
                        elif self.operation == "%":
                            if  self.operator[1] != 0:
                                self.result = float(self.operator[0] %  self.operator[1])
                            else:
                                self.result = "Error"
                        if(self.result != "Error"):
                            self.ta.set_text(str(self.result) + "\n")
                            self.operator = [self.result,None]
                            self.operation = None
                            self.la.set_text("=")
                        else:
                            self.ta.set_text(self.result)
                            self.result = None
                            self.operator = [None,None]
                            self.operation = "="
                            self.la.set_text(self.operation)

        elif txt == "/":  #divide  
            if  self.operator[0] == None:
                self.get_operator()
                self.operation = "/"
                self.la.set_text(self.operation)
            elif  self.operator[1] == None:
                if self.check_op("/"):
                    if self.get_operator(2): 
                        if  self.operator[1] == 0:  #Zero check
                            self.ta.set_text("Error")
                            self.operator = [None,None]
                            self.operation = "="
                            self.la.set_text(self.operation)
                        else:       
                            print(" {} {} {}".format(self.operator[0], self.operation,  self.operator[1]))        
                            self.result = float(self.operator[0] /  self.operator[1])
                            self.end_calc("/")
        
        elif txt == "%":  # mod  
            if  self.operator[0] == None:
                self.get_operator()
                self.operation = "%"
                self.la.set_text(self.operation)
            elif  self.operator[1] == None:
                if self.check_op("%"):
                    if self.get_operator(2):
                        if  self.operator[1] == 0:  #Zero check
                            self.ta.set_text("Error")
                            self.operator = [None,None]
                        else:   
                            print(" {} {} {}".format(self.operator[0], self.operation,  self.operator[1]))            
                            self.result = float(self.operator[0] %  self.operator[1])
                            self.end_calc("%")

        elif txt == lv.SYMBOL.CLOSE: # multiply
            if  self.operator[0] == None:
                self.get_operator()
                self.operation = lv.SYMBOL.CLOSE
                self.la.set_text(self.operation)
            elif  self.operator[1] == None:
                if self.check_op(lv.SYMBOL.CLOSE):
                    if self.get_operator(2):
                        print(" {} {} {}".format(self.operator[0], self.operation,  self.operator[1]))                
                        self.result = float(self.operator[0] *  self.operator[1])
                        self.end_calc(lv.SYMBOL.CLOSE)

        elif txt == lv.SYMBOL.PLUS: #add
            if  self.operator[0] == None:
                self.get_operator()
                self.operation = lv.SYMBOL.PLUS
                self.la.set_text(self.operation)
            elif  self.operator[1] == None:
                if self.check_op(lv.SYMBOL.PLUS):
                    if self.get_operator(2):    
                        print(" {} {} {}".format(self.operator[0], self.operation,  self.operator[1]))           
                        self.result = float(self.operator[0] +  self.operator[1])
                        self.end_calc(lv.SYMBOL.PLUS)

        elif txt == lv.SYMBOL.MINUS: #subtract
            if  self.operator[0] == None:
                self.get_operator()
                self.operation = lv.SYMBOL.MINUS
                self.la.set_text(self.operation)
            elif  self.operator[1] == None:
                if self.check_op(lv.SYMBOL.MINUS):
                    if self.get_operator(2):  
                        print(" {} {} {}".format(self.operator[0], self.operation,  self.operator[1]))              
                        self.result = float(self.operator[0] -  self.operator[1])
                        self.end_calc(lv.SYMBOL.MINUS)

        elif txt:
            self.ta.add_text(txt)
            #lv.event_send(ta, lv.EVENT.READY, None)


#app = CALC_APP()
#app.setup(lv.scr_act())