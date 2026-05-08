#include "linux/gfp_types.h"
#include <linux/fs.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

MODULE_AUTHOR("p.howe & k4lizen");
MODULE_DESCRIPTION("🚜");
MODULE_LICENSE("GPL");

#define PROC_NAME "furrow"

struct furrow {
  uint64_t bed1;
  uint64_t bed2;
  uint64_t bed3;
  uint64_t bed4;
};

int stage = 0;
struct furrow* furrow_obj;

static long furrow_ioctl(struct file* file, unsigned int cmd,
                             unsigned long arg) {
  if (stage == 0) {
    stage += 1;
    // till the dirt
    furrow_obj = (struct furrow*)kmalloc(0x100, GFP_KERNEL);
    memset((void*)furrow_obj, 'T', 0x100);
  } else if (stage == 1) {
    stage += 1;
    // oh noes a storm!
    kfree(furrow_obj);
  } else if (stage == 2) {
    // this one was under cover, needs watering still :3
    furrow_obj->bed4 += 1;
  } else {
    return -EINVAL;
  }
  return 0;
}

static const struct proc_ops fops = {
  .proc_ioctl = furrow_ioctl,
};

static struct proc_dir_entry* proc_entry;

static int __init furrow_init(void) {
  proc_entry = proc_create(PROC_NAME, 0666, NULL, &fops);
  return 0;
}

static void __exit furrow_exit(void) {
  remove_proc_entry(PROC_NAME, NULL);
}

module_init(furrow_init);
module_exit(furrow_exit);
