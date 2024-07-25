# MaterialX_Convert

## 概要
Mayaで作成したマテリアルをMaterialXに変換するツールです。
## 要件
[pymel](https://github.com/LumaPictures/pymel)
## 使い方
1.ドキュメントのmaya/使用バージョン/script内に.pyファイルを移動する。  
2.以下のコマンドを実行する。
```
import materialX_Convert
materialX_Convert.openWindow()
```
## 説明
1.Maya上でStandardSurface（AiStandardSurface）のマテリアルを作成。  
2.Hypershadeからマテリアルを選択する。（一度に変換できるマテリアルの数は一つ）  
3.保存先のフォルダ、保存するファイル名を設定。  
　テクスチャ画像を別フォルダにコピーするか、絶対パスにするかの設定、  
　画像の保存先を設定する（デフォルトはmtlxと同階層に"Texture"フォルダを作成）  
4."Create" ボタンで実行する。
## 作者
[Twitter](https://x.com/cotte_921)

## ライセンス
[MIT](LICENSE)
