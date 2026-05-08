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
            if(maybe_flag.length() != REPLACE2){
                textView.setText("flag is wrong...");
            } else {
                REPLACE
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
