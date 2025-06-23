package com.example.zilant

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import java.io.File

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val jni = ZilantJNI()
        val cache = cacheDir.absolutePath + "/unzil"
        File(cache).mkdirs()
        val key = ByteArray(32) { 0 }
        jni.unpackDir("sample.zil", cache, key)
        val files = File(cache).list()?.joinToString("\n") ?: "none"
        title = files
    }
}
