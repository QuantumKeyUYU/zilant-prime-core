package com.example.zilant

class ZilantJNI {
    companion object {
        init { System.loadLibrary("zilant") }
    }
    external fun unpackDir(input: String, output: String, key: ByteArray): Int
}
