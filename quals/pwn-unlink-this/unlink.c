#include <stdio.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h> 
#include <string.h>
#include <errno.h>
#include <jemalloc/jemalloc.h>

typedef struct crypto_thing{
    size_t sig_counter;
    int (*sign)(void* crypto_thing, char* buf, size_t len, char* out);
    char* (*allocate_sig)(); 
    void (*destroy_sig)(char* sig); 
}crypto_thing;

typedef struct some_thing{
    size_t next;
    size_t prev;
    int session_id;
    size_t challenge_len;
    char challenge[0x100];
}some_thing;

size_t nr_things = 0;
long list_inited = 0;
some_thing* head_next;
some_thing* head_prev;
crypto_thing* crypto;

int gen_session(){
   return random(); 
}

size_t get_number() {
  size_t n = 0;
  scanf("%zu%*c",&n);
  return n;
}

void linkin(some_thing* new){
    if(!list_inited){
        list_inited = 1;
        head_next = &head_next;
        head_prev = &head_next;
    }
    new->next = &head_next;
    new->prev = head_prev;
    head_prev->next = new;
    head_prev = new; 
}

void unlinnk(some_thing* old){
    some_thing* next = old->next;
    some_thing* prev = old->prev;
    prev->next = old->next;
    next->prev = old->prev;
    old->prev = 0xdeadbeef;
    old->next = 0xdeadbeef;
}

some_thing* find_thing(int session_id){
    some_thing* curr = head_next;
    while(curr != &head_next){
        if(curr->session_id == session_id) return curr;
        curr = curr->next;
    }
    return NULL;
}

void create(){
    if(nr_things>10){
        puts("too many things!");
        return;
    }
    puts("input size?");
    char in[0x400];
    memset(in, 0, 0x400);
    size_t size = get_number();         
    if(size > 0x400){
        return;
    }
    puts("data?");
    read(0, in, size);
    some_thing* newthing = (some_thing*)malloc(sizeof(some_thing));
    newthing->session_id = gen_session();
    memcpy(newthing->challenge, in, strlen(in));
    newthing->challenge_len = (strlen(in) > 0x100) ? 0x100 : strlen(in); 
    linkin(newthing);
    nr_things++;
    printf("new session: %d\n", newthing->session_id);
}

void sign(){
    puts("session id?");
    int session_id = (int)get_number();
    some_thing* thing = find_thing(session_id);
    if(thing == NULL){
        return;
    }
    char* sig_buf = crypto->allocate_sig();
    crypto->sign(crypto, thing->challenge, thing->challenge_len, sig_buf); 
    puts("challenge: ");
    puts("=============================");
    write(1, thing->challenge, thing->challenge_len);
    puts("\n=============================");
    puts("signature: ");
    puts("=============================");
    write(1, sig_buf, 0x100); 
    puts("\n=============================");
    unlinnk(thing);
    free(thing);
    nr_things--;
    crypto->destroy_sig(sig_buf);
}

int crypto_sign(crypto_thing* self, char* buf, size_t len, char* out){
    self->sig_counter += 1;
    memset(out, 0, 0x100);
    //TODO
    return 0;
} 

void menu(){
    puts("1: create something");
    puts("2: do sometehing with the thing");
}

int main(){
    srand((unsigned)time(NULL));
    setbuf(stdin,NULL);
    setbuf(stdout,NULL);
    setbuf(stderr,NULL); 
    crypto = (crypto_thing*)malloc(sizeof(crypto_thing));
    crypto->sig_counter = 0;
    crypto->sign = crypto_sign;
    crypto->allocate_sig = malloc;
    crypto->destroy_sig = free;
    while(1){
        menu();
        switch(get_number()){
            case 1: {
                create();
                break;
            } 
            case 2: {
                sign();
                break;
            } 
            default: {
                puts("not an option..");
                break;
            }
        }
    } 
}
