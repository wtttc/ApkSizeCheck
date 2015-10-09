# ApkSizeCheck
Simple py script to check the change of apk size & check images can be optimize to shrink apk.
Python2.7+ is needed.
numpy and Pillow are needed if using apkimagecheck, pip can install it.

```

    sudo pip install -i http://pypi.douban.com/simple/ Pillow
    ...
    sudo pip install -i http://pypi.douban.com/simple/ numpy
    

```

-----
# apkcompare
## Useage
1. Download it
2. Modify apksizecheck/apk_tree. You can unzip the apk to specify the file. Formatting is encouraged. Weibo apk for example.
    
    ```
    
        {
            "AndroidManifest.xml":0,
            "classes.dex":0,
            "resources.arsc":0,
            "assets":{
                "appmarket.jar":0,
                "browser.jar":0,
                "composer.jar":0,
                ...
                }
        }
        
    ```

    file: 
        
    ```
    
        ...
        "AndroidManifest.xml":0
        ...
    
    ```
        
    floder:
        
    ```
    
        ...
        "assets":{
        ...
        }   

    ```
   
3. cd into the absolute path, run the apkcompare.py script with 
    
    ```
    
        '------------PyTest.py usage:------------'
        '-h, --help     : print help message.'
        '-o, --old      : input old apk file path'
        '-n, --new      : input new apk file path'
        '-s, --single   : input single apk file path, conflict with -o & -n'
        '-t, --top      : show the top "n" file new/removed/changed in apk'
        '----------------------------------------'
 
    ```
    
    for example:
    
    ```
    
        python apkcompare.py -o weibo540.apk -n weibo545.apk
        
    
    ```

4. read output, weibo for example
    
    ```
    
        sinasdk:apkcompare easytang$ python apkcompare.py -o weibo540.apk -n weibo545.apk -t 10
        
        apk_old:weibo540.apk size:36.5 MB
        apk_new:weibo545.apk size:39.1 MB
        start to unzip apk old
        start to unzip apk new
        
        
        ============weibo540==============
        path:/resources.arsc                | size: 1.6 MB       |
        path:/assets                        | size: 79.4 MB      |
        ......
        ============weibo540==============
        
        
        ============weibo545==============
        path:/resources.arsc                | size: 1.7 MB       |
        path:/assets                        | size: 82.2 MB      |
        ......
        ============weibo545==============
        
        
        ============compare result==============
        file:/res/drawable-hdpi             | old: 5.3 MB       | new: 4.9 MB       | changed: -447.9 KB   
        ......
        ============compare result==============
        
        
        ============new file============
        file:/assets/MusicVideoAssets.zip                                 | size: 1.6 MB
        ......
        
        ============removed file============
        ......
                
        ============changed file============
        ......
    
    ```

-----
# apkimagecheck
## Useage
1. Download it
2. cd into the absolute path, run the apkimagecheck.py script with 
    
    ```
    
        '------------apkimagecheck.py usage:------------'
        '-h, --help     : print help message.'
        '-f, --file     : apk file'
        '-a, --alpha    : not 0 (default)-> not check pic with no alpha; 0 -> check'
        '-v, --value    : alpha check value, default 255(check pic without even a little alpha)'
        '-l, --limit    : file size limit in byte (1024 -> 1K)'
        '-i, --ignore9  : not 0 (default)-> ignore .9; 0 -> check .9'
        '----------------------------------------'
    
    ```
    
    for example:
    
    ```
    
         python apkimagecheck.py -f weibo545.apk
        
    
    ```
3. read output, weibo for example

    ```
    
        sinasdk:apksizecheck easytang$ python apkimagecheck.py -f weibo545.apk
        
        apk:weibo545.apk
        start to unzip apk
        
        ============ check size limit ==================
        IMAGE:/assets/offlinemap2.png  size:80.2 KB
        IMAGE:/assets/effects/filter/pictureFilter/localFilter/filters/100/filter_icon.png  size:61.8 KB
        IMAGE:/assets/effects/filter/pictureFilter/localFilter/filters/102/filter_icon.png  size:61.8 KB
        ......
        These files may be too large.(larger than 39.1 KB)
        ============ check size limit ==================
        
        
        ============ check image alpha ==================
        This is not image: weibo545/assets/offlinemap2.png
        
        IMAGE:/assets/effects/filter/pictureFilter/localFilter/filters/100/filter_icon.png
        IMAGE:/assets/effects/filter/pictureFilter/localFilter/filters/102/amber.png
        IMAGE:/assets/effects/filter/pictureFilter/localFilter/filters/102/amber_adjust.png
        ......
        These 59 image(s) may be pngs with no alpha, considering jpeg?
        ============ check image alpha ==================
        
    
    ```

-----
## Fixme
1. 
    <s> Since using dict to compare, result will be not specific enough when **file with the same name in different floders**. </s>
    
    <s> for example </s>
        
        ```
        
            ./lalalal.jar
            ./assets/lalalal.jar
        
        ```
        
    <s> will only show one compare result </s>
2. build path
3. unchecked on linux
4. unable to check method count if not simply dex file or a dex in jar. (should modify method get_method_counts_in_file)
5. Obfuscated resources may interrupt since each file's name changed.