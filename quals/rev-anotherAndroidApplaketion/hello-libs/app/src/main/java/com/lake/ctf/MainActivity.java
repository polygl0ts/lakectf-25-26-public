package com.lake.ctf;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.TextView;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText; import android.widget.LinearLayout;
import android.widget.TextView;
import android.util.Log;

public class MainActivity extends AppCompatActivity {
    public native boolean Test(String in);
    public native long Init();
    static {
        System.loadLibrary("ohgreat2");
    }
    long wow = 0;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        this.wow = Init();
        // Create a vertical LinearLayout
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);

        // Create a TextView for displaying results
        TextView textView = new TextView(this);
        textView.setText("this UI follows swiss style");

        // Create a TextInput (EditText)
        EditText editText = new EditText(this);
        editText.setHint("Enter flag:");

        // Create a Button
        Button button = new Button(this);
        button.setText("Check flag");

        // Set the button click listener
        button.setOnClickListener(v -> {
            // Get the input text
            String maybe_flag = editText.getText().toString();
            // Call the native function with the input text
            Log.i("LAKECTF", "flag: " + maybe_flag);
            if(maybe_flag.length() != 55){
                textView.setText("flag is wrong...");
            } else {
                boolean r0 = Test(maybe_flag);
boolean r1 = Test(maybe_flag);
boolean r2 = Test(maybe_flag);
boolean r3 = Test(maybe_flag);
boolean r4 = Test(maybe_flag);
boolean r5 = Test(maybe_flag);
boolean r6 = Test(maybe_flag);
boolean r7 = Test(maybe_flag);
boolean r8 = Test(maybe_flag);
boolean r9 = Test(maybe_flag);
boolean r10 = Test(maybe_flag);
boolean r11 = Test(maybe_flag);
boolean r12 = Test(maybe_flag);
boolean r13 = Test(maybe_flag);
boolean r14 = Test(maybe_flag);
boolean r15 = Test(maybe_flag);
boolean r16 = Test(maybe_flag);
boolean r17 = Test(maybe_flag);
boolean r18 = Test(maybe_flag);
boolean r19 = Test(maybe_flag);
boolean r20 = Test(maybe_flag);
boolean r21 = Test(maybe_flag);
boolean r22 = Test(maybe_flag);
boolean r23 = Test(maybe_flag);
boolean r24 = Test(maybe_flag);
boolean r25 = Test(maybe_flag);
boolean r26 = Test(maybe_flag);
boolean r27 = Test(maybe_flag);
boolean r28 = Test(maybe_flag);
boolean r29 = Test(maybe_flag);
boolean r30 = Test(maybe_flag);
boolean r31 = Test(maybe_flag);
boolean r32 = Test(maybe_flag);
boolean r33 = Test(maybe_flag);
boolean r34 = Test(maybe_flag);
boolean r35 = Test(maybe_flag);
boolean r36 = Test(maybe_flag);
boolean r37 = Test(maybe_flag);
boolean r38 = Test(maybe_flag);
boolean r39 = Test(maybe_flag);
boolean r40 = Test(maybe_flag);
boolean r41 = Test(maybe_flag);
boolean r42 = Test(maybe_flag);
boolean r43 = Test(maybe_flag);
boolean r44 = Test(maybe_flag);
boolean r45 = Test(maybe_flag);
boolean r46 = Test(maybe_flag);
boolean r47 = Test(maybe_flag);
boolean r48 = Test(maybe_flag);
boolean r49 = Test(maybe_flag);
boolean r50 = Test(maybe_flag);
boolean r51 = Test(maybe_flag);
boolean r52 = Test(maybe_flag);
boolean r53 = Test(maybe_flag);
boolean r54 = Test(maybe_flag);
boolean r55 = Test(maybe_flag);
boolean r56 = Test(maybe_flag);
boolean r57 = Test(maybe_flag);
boolean r58 = Test(maybe_flag);
boolean r59 = Test(maybe_flag);
boolean r60 = Test(maybe_flag);
boolean r61 = Test(maybe_flag);
boolean r62 = Test(maybe_flag);
boolean r63 = Test(maybe_flag);
boolean r64 = Test(maybe_flag);
boolean r65 = Test(maybe_flag);
boolean r66 = Test(maybe_flag);
boolean r67 = Test(maybe_flag);
boolean r68 = Test(maybe_flag);
boolean r69 = Test(maybe_flag);
boolean r70 = Test(maybe_flag);
boolean r71 = Test(maybe_flag);
boolean r72 = Test(maybe_flag);
boolean r73 = Test(maybe_flag);
boolean r74 = Test(maybe_flag);
boolean r75 = Test(maybe_flag);
boolean r76 = Test(maybe_flag);
boolean r77 = Test(maybe_flag);
boolean r78 = Test(maybe_flag);
boolean r79 = Test(maybe_flag);
if(r0 &&r1 &&r2 &&r3 &&r4 &&r5 &&r6 &&r7 &&r8 &&r9 &&r10 &&r11 &&r12 &&r13 &&r14 &&r15 &&r16 &&r17 &&r18 &&r19 &&r20 &&r21 &&r22 &&r23 &&r24 &&r25 &&r26 &&r27 &&r28 &&r29 &&r30 &&r31 &&r32 &&r33 &&r34 &&r35 &&r36 &&r37 &&r38 &&r39 &&r40 &&r41 &&r42 &&r43 &&r44 &&r45 &&r46 &&r47 &&r48 &&r49 &&r50 &&r51 &&r52 &&r53 &&r54 &&r55 &&r56 &&r57 &&r58 &&r59 &&r60 &&r61 &&r62 &&r63 &&r64 &&r65 &&r66 &&r67 &&r68 &&r69 &&r70 &&r71 &&r72 &&r73 &&r74 &&r75 &&r76 &&r77 &&r78 &&r79 &&true) {
textView.setText("flag correct!");

                } else {
                    textView.setText("flag is wrong...");
                }
            }
        });
        // Add views to the layout
        layout.addView(editText);
        layout.addView(button);
        layout.addView(textView);
        // Set the layout as the content view
        setContentView(layout);
    }
}
