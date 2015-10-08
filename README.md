# ApkSizeCompare
Simple py script to check the change of apk size

-----
## Useage
1. Download it
2. Modify apkcompare/apk_tree. You can unzip the apk to specify the file. Formatting is encouraged. Weibo apk for example.
    
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
   
3. cd into the absolute path, run the py script with 
    
    ```
    
        '------------PyTest.py usage:------------'
        '-h, --help     : print help message.'
        '-o, --old      : input old apk file path'
        '-n, --new      : input new apk file path'
        '-s, --single   : input single apk file path, conflict with -o & -n'
        '-t, --topcount : show the top "n" largest new file in apk'
        '----------------------------------------'
 
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
        
        
        ============top 10 large new file============
        file:/assets/MusicVideoAssets.zip                                 | size: 1.6 MB
        ......
    
    ```

-----
## Fixme
build path
unchecked on linux