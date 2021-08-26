# AT&T汇编语法

## 一、汇编的组成
Linux系统的内存被分为如下几段：
text段、data段、bss段、heap段、stack段、内核段
在汇编程序中，一般会由text、data和bss段组成，其中data段又会细分出rodata段

操作码：如mov、jmp
寄存器：x86_64平台拥有16个64位寄存器

## 二、数据格式

在每个操作码op的后面都会有一个字符后缀，表明操作数大小。
b: 1字节 对应char
w: 2字节 对应short
l: 4字节 对应long

## 二、指令格式

```ASM
op[b|w|l] 源寄存器/数据，目标寄存器
```


## 三、寻址方式

