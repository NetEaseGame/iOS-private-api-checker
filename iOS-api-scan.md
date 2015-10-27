## iOS Qzone私有API扫描工作总结

### 背景
苹果提供的iOS开发框架分PrivateFramework和Framework，PrivateFramework下的库是绝对不允许在提交的iOS应用中使用的，只允许使用Framework下那些公开的库。除了不能引入私有的库，也不能使用私有的API。如果你做了，结果很明显，你的应用就会被拒掉。
#####下面是几个被拒的案例：
1. **案例1**([来源于网络](http://www.cocoachina.com/bbs/read.php?tid=12514&page=1))
>Thank you for submitting your update to xxx to the App Store.  During our review of your application we found it is using a private API, which is in violation of the iPhone Developer Program License Agreement section 3.3.1; `"3.3.1 Applications may only use Documented APIs in the manner prescribed by Apple and must not use or call any private APIs."` **While your application has not been rejected, it would be appropriate to resolve this issue in your next update.**
>
>"3.3.1 Applications may only use Documented APIs in the manner prescribed by Apple and must not use or call any private APIs."
>
>The non-public API that is included in your application is **`terminateWithSuccess`**.
>
>If you have defined a method in your source code with the same name as the above mentioned API, we suggest altering your method name so that it no longer collides with Apple's private API to avoid your application being flagged with future submissions.
>
>Please resolve this issue in your next update to xxx.
>
>Regards,
>
>iPhone Developer Program

	很幸运，使用了重名的API但是没被拒，不过Apple还是建议下次更新时要修改那个API的名字。
2. 案例2（[来源于网络](http://stackoverflow.com/questions/18756906/apple-reject-my-app-because-using-private-api-allowsanyhttpscertificateforhos)）
>We found that your app uses one or more non-public APIs, which is not in compliance with the App Store Review Guidelines. The use of non-public APIs is not permissible because it can lead to a poor user experience should these APIs change.
>
>We found the following non-public API/s in your app:
>
>**`allowsAnyHTTPSCertificateForHost:`**
>
If you have defined methods in your source code with the same names as the above-mentioned APIs, we suggest altering your method names so that they no longer collide with Apple's private APIs to avoid your application being flagged in future submissions.
>
Additionally, one or more of the above-mentioned APIs may reside in a static library included with your application. *If you do not have access to the library's source, you may be able to search the compiled binary using "`strings`" or "`otool`" command line tools.* The "strings" tool can output a list of the methods that the library calls and "otool -ov" will output the Objective-C class structures and their defined methods. These techniques can help you narrow down where the problematic code resides.

	这位就没那么幸运了，被拒了，不过Apple还算人性化，提供了方法来解决办法。
3. 案例3（Qzone）
   
   同样是因为	使用了一个私有的API，不过我们感觉有点冤，我们只是放那里并没有调用,`[self performSelector:@selector(_define:) withObject:obj afterDelay:10]`,一切被拒的原因都是因为`_define:`，这个api是私有的，苹果的文档里没有这个api，也不是我们自己定义的函数，被认为调用了私有api。
   
这些都是教训啊，在今后iOS过程中要避免因为私有api问题而被拒啊。可怎么避免呢？哪些api又是私有的呢？私有的api又放在哪里呢？

鉴于以上的问题有了这里针对私有api扫描的探索工作。


### 漫漫探索路

#### 哪些是私有的api?私有的api又放在哪里？
苹果官方也没有结出明确的定义，我们估且从反面来考虑，官方给出了有文档的api(也就是建议开发者使用的)，同时也有提及没有文档的api(不建议使用的，可能随时会被修改或移除)。带文档的api我们可以方便的从Xcode的帮助里查看，不带文档的从帮助文档当然是查不到的，但是在Framework下的头文件里会有声明，可以从相应头文件里查看，例如`valueForPasteboardType:`,存在于`UIKit.framework/UIPasteboard.h`里。

难道api就只有这些吗？答案肯定不是喽。我们还没有找到私有的api呢。在前面我们有提到PrivateFramework，这下面的库都是私有的，苹果不允许你使用的，当然里面定义的方法也自然成为了私有api的一份子。除了PrivateFramework下的api，其他的在哪呢？当然是在公开的让你使用的Framwork下了，只是没有公开，你看不到罢了。但是看不到不代表不存在啊。我们只使用了公开的库，确以使用私有api的理由拒我们。那所使用的私有api来自何方？必须来自公开的库啊。

在公开的Framework下定义了很多不为人知的类及方法（一般人我不告诉他^-^）。但是通过一般的方法我们是看不到他们的，那我们就采取点非常手段吧。[`class-dump`](stevenygard.com/projects/class-dump/)上台，class-dump可以查看Mach-O文件里的OC运行时信息。我们就来试试水吧。class-dump请自行解决下载安装。
<pre>
class-dump -H /Applications/Xcode.app/Contents/Developer/Platforms/	iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/	Frameworks/UIKit.framework -o ./UIKit</pre>
通过这条命令我们可以得到UIKit下定义的所有类的信息，并在UIKit目录(随意指定目录即可)下生成相应的头文件。统计下生成的头文件有13400个，真实情况可能没有这么多，因为class-dump为每个interface，protocol以及category都会生成一个头文件，而在*UIKit.framework/Header/\*.h* 下只有137个头文件，由此可见，即使是公开的Framework,也隐藏很多不为人知的东西。

从我们class-dump出来的头文件可以看到有些以 _ 开头，这些是私有的错不了。我们再窥探下头文件的内部都有些啥。
下面是`UITextView.h`的部分内容。
<pre>
#import "UIKeyboardInput.h"
....
@class .....
@interface UITextView : UIScrollView <UITextLinkInteraction, UITextInputControllerDelegate, UITextAutoscrolling, UIKeyboardInput, UITextInput>
{
    id _private;
    NSTextStorage *_textStorage;
    ...
    UIView *_inputAccessoryView;
}
+ (id)_bestInterpretationForDictationResult:(id)arg1;
+ (_Bool)_isCompatibilityTextView;
+ (id)_sharedHighlightView;
@property(readonly, nonatomic) NSTextStorage *textStorage; // @synthesize textStorage=_textStorage;
- (void)_resetDataDetectorsResults;
- (void)_startDataDetectors;
- (id)automaticallySelectedOverlay;
- (void)keyboardInputChangedSelection:(id)arg1;
- (_Bool)keyboardInputChanged:(id)arg1;
- (_Bool)keyboardInputShouldDelete:(id)arg1;
- (void)_promptForReplace:(id)arg1;
- (void)_showTextStyleOptions:(id)arg1;
- (_Bool)_isDisplayingReferenceLibraryViewController;
- (void)_define:(id)arg1;
- (void)dealloc;
- (void)_populateArchivedSubviews:(id)arg1;
- (void)encodeWithCoder:(id)arg1;
- (void)_commonInitWithTextContainer:(id)arg1 isDecoding:(_Bool)arg2 isEditable:(_Bool)arg3 isSelectable:(_Bool)arg4;
- (_Bool)isElementAccessibilityExposedToInterfaceBuilder;
- (_Bool)isAccessibilityElementByDefault;
- (void)drawRect:(struct CGRect)arg1 forViewPrintFormatter:(id)arg2;
- (Class)_printFormatterClass;
@property(nonatomic, setter=_setDrawsDebugBaselines:) _Bool _drawsDebugBaselines;
....
@end
</pre>

从上面的代码中可以看到有很多函数是以 _ 开头的，这些也是私有的，像我们在案例3中提到的`_define:`，就出现在了这里。但是不以 _ 开头的也不能说不是私有的，像`keyboardInputShouldDelete:`这个，不以_开头，但是是私有的api。由此印证了我们之前的猜测，公开的库里存在大量的私有api。

通过以上的分析，我们可以对私有api来做个总结了。
#####小结
1. `私有的api ＝ (class-dump Framework下的库生成的头文件中的api - (Framework下的头文件里的api = 有文档的api + 没有文档的api)) + PrivateFramework下的api`。
2. 私有的api在公开的Framework及私有的PrivateFramework都有。

#### 构建私有API库

既然已经知道的哪些是私有的api及私有api的位置，就可以建立私有api的专用数据库了。

具体步骤：

1. 用`class-dump`对所有的公开库(/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks)进行逆向工程得到所有的头文件内容。提取每个.h文件中的api得到api集合`set_A`。
2. 获得带文档的api。Xcode自带帮助文档，从那里查到的api自然是带文档的了，怎么获得这些文档呢？记得在Xcode3的时候查个文档会特别的慢，现在的Xcode5再查某个api的时候很快就会出结果，肯定对api检索做了优化，在某处放着api的索引。这个想法也是受了`Dash`这个工具的启发，Dash中也可以查看iOS的api，但是帮助文档不是自己管理的，直接查的Xcode中带的文档，按图索骥找到Xcode的文档位置(/Users/sngTest/Library/Developer/Shared/Documentation/DocSets/com.apple.adc.documentation.AppleiOS7.0.iOSLibrary.docset/Contents/Resources),在里面有个`docSet.dsidx`的文件，这就是Xcode针对api做的数据库，从这里可以获得带文档的api的各种信息了，从而有了带文档的api集合`set_B`。
3. 现在需要获得那些没有文档的公开api了，从上面的分析知道他们存在于公开的库的头文件中，所以要对这些公开的头文件进行扫描，提取那些没有文档的api，这里得到的集合会第2步得到的集合有很大部分是重复的，这不影响最终结果，得到集合`set_C`。
4. 得到最终的私有api集合 `set = set_A - set_B - set_C`。

#### 针对Qzone进行具体的扫描工作

1. 将Qzone.ipa解压，得到Payload文件夹，用`strings`工具对`Payload/Qzone.app/Qzone`(这是个Mach-O文件)扫描，得到程序中可见的字符串**`strings`**。这里截取部分strings结果:<pre>
encodeInt:forKey:
rain
setRain:
initWithFrame:
...
_subscribeBtn
...
playing gif count statistics error
stop gif, total playing count***********(%d)
targetOrient
Ti,D,N
video
T@"Video",&,N
zoomAspect
TB,D,N
context
T@"EAGLContext",&,N,Vcontext
animationInterval
Td,VanimationInterval
...
</pre>这里的strings结果中有定义的OC方法，属性，hardcode字符串，及其他编译时加入的代码。可以先从已知的进行排除，像hardcode字符串，可以通过扫描代码提取这部分字符串。
2. 扫描源码，获得hardcode字符串，得到结果集**`str_set`**。
3. 获得程序中自己定义的方法。这里使用`otool`，用`nm`也可以拿到方法，但是不能拿到属性及变量，所以这里用otoo拿到方法，属性及变量。`otool -ov ../../../Qzone`,截取部分进行说明:<pre>
Contents of (\_\_DATA,\_\_objc_classlist) section   **// 这里是程序中自己定义的所有类的开始部分**
01dcf12c 0x1f62b30 \_OBJC\_CLASS\_$\_QZFlowerInfo
           isa 0x1f62b44 \_OBJC_METACLASS_$_QZFlowerInfo
    superclass 0x1f6b1b8 \_OBJC_CLASS_$_QZBaseWidgetInfo
         cache 0x0
        vtable 0x0
          data 0x1dd22c0 (struct class_ro_t \*)
                    flags 0x184 RO_HAS_CXX_STRUCTORS
            instanceStart 4
             instanceSize 24
               ivarLayout 0x1cc43f6
                layout map: 0x41 
                     name 0x1cc43e9 QZFlowerInfo
              baseMethods 0x1dd2180 (struct method_list_t \*)
		   entsize 12
		     count 13
		      name 0x1b09ceb encodeWithCoder:  **//定义的一般方法**
		     types 0x1cd4287 v12@0:4@8
		       imp 0xaf85
		       name 0x1b09c38 sun       **//这里是property sun 的getter方法**
		     types 0x1cd42a2 i8@0:4
		       imp 0xb38d
		      name 0x1b09c9d setSun:   **//这里是property sun 的setter方法**
		     types 0x1cd42a9 v12@0:4i8
		       imp 0xb3a9
		     name 0x1b09c63 flowerpicurl
		     types 0x1cd42b3 @8@0:4
		       imp 0xb47d
		      name 0x1b09cda setFlowerpicurl:
		     types 0x1cd4287 v12@0:4@8
		       imp 0xb499
            baseProtocols 0x0
                    ivars 0x1dd2224 **// 这里是定义的变量**
                    entsize 20
                      count 5
			   offset 0x1fbb620 4
			     name 0x1b09c38 sun
			     type 0x1cd42ba i
			alignment 2
			     size 4
			   offset 0x1fbb624 8
			     name 0x1b09c4e rain
			     type 0x1cd42ba i
			alignment 2
			     size 4
			   offset 0x1fbb628 12
			     name 0x1b09c53 love
			     type 0x1cd42ba i
			alignment 2
			     size 4
			   offset 0x1fbb62c 16
			     name 0x1b09c58 fertilizer
			     type 0x1cd42ba i
			alignment 2
			     size 4
			   offset 0x1fbb630 20
			     name 0x1b09c63 flowerpicurl
			     type 0x1cd42bc @"NSString"
			alignment 2
			     size 4
           weakIvarLayout 0x0
           baseProperties 0x1dd2290   **// 这里是定义的属性**
                    entsize 8
                      count 5
			     name 0x1ba4f40 sun
			attributes x1ba4f66 Ti,N,Vsun
			     name 0x1ba4f44 rain
			attributes x1ba4f70 Ti,N,Vrain
			     name 0x1ba4f49 love
			attributes x1ba4f7b Ti,N,Vlove
			     name 0x1ba4f4e fertilizer
			attributes x1ba4f86 Ti,N,Vfertilizer
			     name 0x1ba4f59 flowerpicurl
			attributes x1ba4f97 T@"NSString",&,N,Vflowerpicurl
			.....
Contents of (\_\_DATA,\_\_objc_catlist) section   **//这里开始category**
01dd1878 0x1ead610    **//这里定义了某个类的category, 有定义属性**
              name 0x1cccb53
               cls 0x0
   instanceMethods 0x1ead5a8
		   entsize 12
		     count 6
		      name 0x1b6d83b addInfiniteScrollingWithActionHandler:
		     types 0x1cd669b v12@0:4@?8
		       imp 0x10feda1
		      name 0x1b6d862 triggerInfiniteScrolling
		     types 0x1cd429b v8@0:4
		       imp 0x10ff0e5
		      name 0x1b6d7a0 setInfiniteScrollingView:
		     types 0x1cd4287 v12@0:4@8
		       imp 0x10ff19d
		      name 0x1b6d755 infiniteScrollingView
		     types 0x1cd42b3 @8@0:4
		       imp 0x10ff265
		      name 0x1b6d7ba setShowsInfiniteScrolling:
		     types 0x1cd4581 v12@0:4c8
		       imp 0x10ff285
		      name 0x1b6d87b showsInfiniteScrolling
		     types 0x1cd4454 c8@0:4
		       imp 0x10ff8dd
      classMethods 0x0
         protocols 0x0
instanceProperties 0x1ead5f8
                    entsize 8
                      count 2
			     name 0x1c388fb infiniteScrollingView   **// 定义某个类的私有属性**
			attributes x1c38911 T@"SVInfiniteScrollingView",R,D,N
			     name 0x1c38933 showsInfiniteScrolling
			attributes x1c55f92 Tc,N
01dd1784 0x1dd89bc          **//这里定义了某个类的category, 没有定义属性**
              name 0x1cc4993
               cls 0x0
   instanceMethods 0x1dd897c
		   entsize 12
		     count 2
		      name 0x1b1269c fontHeight
		     types 0x1cd51a0 f8@0:4
		       imp 0xbf21d
		      name 0x1b126a7 defaultLineHeight
		     types 0x1cd51a0 f8@0:4
		       imp 0xbf281
      classMethods 0x1dd899c
		   entsize 12
		     count 2
		      name 0x1b126b9 boldSystemFontVerdanaOfSize:
		     types 0x1cd5d02 @12@0:4f8
		       imp 0xbf17d
		      name 0x1b126d6 systemFontVerdanaOfSize:
		     types 0x1cd5d02 @12@0:4f8
		       imp 0xbf1cd
         protocols 0x0
instanceProperties 0x0
...
Contents of (\_\_DATA,\_\_objc\_classrefs) section  **//定义的类**
01f5e8ec 0x1f6c3b0 \_OBJC\_CLASS\_$\_QzoneGuidePageView
01f5e8f8 0x1f66cd0 \_OBJC\_CLASS\_$\_QzoneGuideView
01f5e900 0x1f780e8 \_OBJC\_CLASS\_$\_WnsLogger
...
Contents of (\_\_DATA,\_\_objc_superrefs) section  **//定义的父类**
01f60b4c 0x1f62b30 \_OBJC\_CLASS\_$\_QZFlowerInfo
01f60b50 0x1f62b58 \_OBJC\_CLASS\_$\_QQGuideWindow
01f60b54 0x1f62b80 \_OBJC\_CLASS\_$\_QzoneNewFeedDetailManager
01f60b58 0x1f62ba8 \_OBJC\_CLASS\_$\_inputBarCacheObject
...
</pre>从上面的分析可以提取出方法，变量(**`set_B_i`**)，属性(**`set_B_p`**)，类名(**`set_B_c`**)了。
4. 用`nm ../../Qzone`得到Mach-O中的符号表。<pre>
0116f0ac t +[AFHTTPClient clientWithBaseURL:]
0117cb08 t +[AFHTTPRequestOperation acceptableContentTypes]
0117c7c8 t +[AFHTTPRequestOperation acceptableStatusCodes]
...
011e20fc t +[NSNumber(uniAttribute) boolValueWithName:inAttributes:]
011e2288 t +[NSNumber(uniAttribute) charValueWithName:inAttributes:]
011e2a90 t +[NSNumber(uniAttribute) doubleValueWithName:inAttributes:]
...
</pre>很容易提取出类名与对应的方法,**`set_C`**。
5. 查看应用都使用了哪些库，`otool -L ../.../Qzone`会看到使用的库**`set_Libs`**。
6. 从上面建立的私有api库中查询所有属于`set_Libs`的api，与步骤4中得到的方法做一个交集，得到了程序中定义的与私有api重名的那些api(set_Method)，至于这些api是否真的会导致被拒，需要人工审核差建立白名单，暂且称他们为**waring_apis**。<pre>
APINAME  selectionChanged
\------------------------------------------------------------ 库中定义相同方法的头文件
UITextInteractionAssistant	UITextInteractionAssistant.h	UIKit.framework
UITextSelection	UITextSelection.h	UIKit.framework
UITextSelectionView	UITextSelectionView.h	UIKit.framework
UIWebDocumentView	UIWebDocumentView.h	UIKit.framework
UIWebSelection	UIWebSelection.h	UIKit.framework
UIWebSelectionAssistant	UIWebSelectionAssistant.h	UIKit.framework
UIWebSelectionView	UIWebSelectionView.h	UIKit.framework
\------------------------------   程序中定义该方法的类
=> 	 [DLTextView  selectionChanged]
=> 	 [RichTextView  selectionChanged]
=> 	 [DLTextContainerView  selectionChanged]
</pre>
7. 现在程序中自己定义的方法已经扫描结束了，但是如果程序中引用第三方库呢，还要扫描所用的第三方库是否用了私有的api，像之前facebook开源的Three20框架，因定义了很多与私有api重名的方法，导致很多基于该框架的应用被拒。从第一步中得到的`rest_str = strings - str_set - set_B_i - set_B_p - set_B_c`。将rest_str与步骤6中查询得到的api列表相交，这个结果集(set_Rest)就是来自第三方的库，但是如果没有第三方库的源码，不容易判断这些交集是属于方法还是hardcode的字符串。为进一步确定他们是来自哪个库，可以strings每个三方库，然后与set_Rest相交，得到每个三方库中命中的strings。如：<pre>
WnsSDK 
\--------------------------------------------------
pasteboard
random
tag:
reconnect
table
apply
pointer
generator
add
call
take
postalAddress
read
emailAddress
pair
now
types
Comment
Secure
bind
adapter
curve
remove
signature
order
</pre>以上即当前对Qzone进行的扫描工作。

#####总结
通过以上各种方法，虽然可以看到某些可能“危险”的api, 但是结果还不是非常满意，需要人工来判断。还是需要再找找其他的方法，优化扫描结果。

写在最后，感谢pettychen & wisonlin 的指导与帮助。