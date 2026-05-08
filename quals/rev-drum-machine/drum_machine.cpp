#include <iostream>
#include <stdint.h>
#include <vector>
#include "drum_machine.h"
#include <string>

using namespace std;

std::vector<Step> decomposeInput(const std::string &input) {
    std::vector<Step> steps;
    for (int i = 0; i < min((int) input.length(), 42); i++) {
        char c = input[i];
        for (int j = 0; j < 8; j++) {
            int s = (c >> j) & 0x01;
            if (s) {
                Step step;
                step.setHit(static_cast<DrumInstrument>(j));
                steps.push_back(step);
            }
        }
    }
    return steps;
}

int main() {
    DrumMachine drumMachine;
    vector<Step> playerSteps;
    string input;

    cout << "Welcome to the polygl0ts Drum Machine!" << endl;
    cout << "During this machine's conception, we managed to create what we believe is the most magical beat invented" << endl;
    cout << "If you are able to recreate it, we will give you the flag!" << endl;
    cout << "Please input your beat sequence: ";
    cin >> input;

    playerSteps = decomposeInput(input);

    drumMachine.setSteps(playerSteps);
    drumMachine.playBeat();

    int state = drumMachine.getState();
    if (state == 181) {
        cout << "Congratulations! You were able to recreate our magical beat. Isn't it great?" << endl;
    } else {
        cout << "This beat is not really magical..." << endl;
    }

    exit(0);
}