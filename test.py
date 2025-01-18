from tkinter import *
import random
from tkinter import ttk

window=Tk()
window.title('ProjectGurukul Memory Game')

#-------------------------------------------------------------level1-----------------------------------------------------------------
tabs = ttk.Notebook(window) 
root= ttk.Frame(tabs)

def draw(c,i,j):
    global base
    if c=='A':
        d=base.create_rectangle(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='red')
    elif c=='B':
        d=base.create_rectangle(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='yellow')
    elif c=='C':
        d=base.create_rectangle(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='blue')
    elif c=='D':
        d=base.create_oval(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='red')
    elif c=='E':
        d=base.create_oval(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='yellow')
    elif c=='F':
        d=base.create_oval(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='blue')
    elif c=='G':
        d=base.create_polygon(100*i+50,j*100+20,100*i+20,100*j+100-20,100*i+100-20,100*j+100-20,fill='red')
    elif c=='H':
        d=base.create_polygon(100*i+50,j*100+20,100*i+20,100*j+100-20,100*i+100-20,100*j+100-20,fill='green')
    
def displayBoard():
    global base,ans,board,moves
    cnt=0
    for i in range(4):
        for j in range(4):
            rect=base.create_rectangle(100*i,j*100,100*i+100,100*j+100,fill="lavender")
            if(board[i][j]!='.'):
                draw(board[i][j],i,j)
                cnt+=1
    if cnt==16:
        base.create_text(200,450,text="Moves: "+str(moves),font=('arial',20))

            

def callback(event):
    global base,ans,board,moves,prev
    #print ("clicked at", event.x, event.y)
    i=event.x//100
    j=event.y//100
    if board[i][j]!='.':
        return
    # if prev is invalid 
    moves+=1
    #print(moves)
    if(prev[0]>4):
        prev[0]=i
        prev[1]=j
        board[i][j]=ans[i][j]
        displayBoard()
    else:
        board[i][j]=ans[i][j]
        displayBoard()
        if(ans[i][j]==board[prev[0]][prev[1]]):
            print("matched")
            prev=[100,100]
            displayBoard()
            return
        else:
            board[prev[0]][prev[1]]='.'
            displayBoard()
            prev=[i,j]
            return

base=Canvas(root,width=500,height=500)
base.pack()

ans = list('AABBCCDDEEFFGGHH')
random.shuffle(ans)
ans = [ans[:4],
       ans[4:8],
       ans[8:12],
       ans[12:]]

base.bind("<Button-1>", callback)

moves=IntVar()
moves=0

prev=[100,100]

board=[list('.'*4) for cnt in range(4)]
displayBoard()

#-------------------------------------------------------------level2-----------------------------------------------------------------
root2= ttk.Frame(tabs)
  
tabs.add(root, text ='Easy') 
tabs.add(root2, text ='Hard') 
tabs.pack(expand = 1, fill ="both") 

def draw2(c,i,j):
    global base2
    if c=='A':
        d=base2.create_rectangle(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='red')
    elif c=='B':
        d=base2.create_rectangle(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='yellow')
    elif c=='C':
        d=base2.create_rectangle(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='blue')
    elif c=='D':
        d=base2.create_oval(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='red')
    elif c=='E':
        d=base2.create_oval(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='yellow')
    elif c=='F':
        d=base2.create_oval(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='blue')
    elif c=='G':
        d=base2.create_polygon(100*i+50,j*100+20,100*i+20,100*j+100-20,100*i+100-20,100*j+100-20,fill='red')
    elif c=='H':
        d=base2.create_polygon(100*i+50,j*100+20,100*i+20,100*j+100-20,100*i+100-20,100*j+100-20,fill='green')
    elif c=='I':
        d=base2.create_polygon(100*i+50,j*100+20,100*i+20,100*j+100-20,100*i+100-20,100*j+100-20,fill='yellow')
    elif c=='J':
        d=base2.create_polygon(100*i+50,j*100+20,100*i+20,100*j+100-20,100*i+100-20,100*j+100-20,fill='blue')
    elif c=='K':
        d=base2.create_polygon(100*i+50,j*100+20,100*i+20,100*j+100-20,100*i+100-20,100*j+100-20,fill='black')
    elif c=='L':
        d=base2.create_polygon(100*i+50,j*100+20,100*i+20,100*j+100-20,100*i+100-20,100*j+100-20,fill='orange')
    elif c=='M':
        d=base2.create_rectangle(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='black')
    elif c=='N':
        d=base2.create_rectangle(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='orange')
    elif c=='O':
        d=base2.create_rectangle(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='green')
    elif c=='P':
        d=base2.create_oval(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='black')
    elif c=='Q':
        d=base2.create_oval(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='orange')
    elif c=='R':
        d=base2.create_oval(100*i+20,j*100+20,100*i+100-20,100*j+100-20,fill='green')
    

    
def displayboard2():
    global base2,ans2,board2,moves2
    cnt=0
    for i in range(6):
        for j in range(6):
            rect=base2.create_rectangle(100*i,j*100,100*i+100,100*j+100,fill="lavender")
            if(board2[i][j]!='.'):
                draw2(board2[i][j],i,j)
                cnt+=1
    if cnt>=36:
        #print("cnt------------------------",cnt)
        base2.create_text(300,650,text="Moves: "+str(moves2),font=('arial',20))

            

def callback2(event):
    global base2,ans2,board2,moves2,prev2
    #print ("clicked at", event.x, event.y)
    i=event.x//100
    j=event.y//100
    if board2[i][j]!='.':
        return
    # if prev2 is invalid 
    moves2+=1
    #print(moves2)
    if(prev2[0]>6):
        prev2[0]=i
        prev2[1]=j
        board2[i][j]=ans2[i][j]
        displayboard2()
    else:
        board2[i][j]=ans2[i][j]
        displayboard2()
        if(ans2[i][j]==board2[prev2[0]][prev2[1]]):
            print("matched")
            prev2=[100,100]
            displayboard2()
            return
        else:
            board2[prev2[0]][prev2[1]]='.'
            displayboard2()
            prev2=[i,j]
            return

base2=Canvas(root2,width=1000,height=1000)
base2.pack()


ans2 = list('AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRR')
random.shuffle(ans2)
ans2 = [ans2[:6],
       ans2[6:12],
       ans2[12:18],
       ans2[18:24],
       ans2[24:30],
       ans2[30:]
       ]

base2.bind("<Button-1>", callback2)

moves2=IntVar()
moves2=0

prev2=[100,100]

board2=[list('.'*6) for cnt in range(6)]
displayboard2()

window.mainloop()