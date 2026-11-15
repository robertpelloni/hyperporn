#include <stdio.h>
#include <string.h>
#include "tvai.h"

int main(int argc, char **argv) {
    const char *dir = argc > 1 ? argv[1] : "topaz-models";
    tvai_set_logging(1);
    int ok = tvai_setup_model_manager((char *)dir, (char *)dir, 1);
    printf("setup_model_manager=%d\n", ok);
    printf("owns_app=%d owns_pro=%d license_type=%d\n",
           tvai_owns_app(), tvai_owns_pro(), tvai_license_type());
    char user[256] = {0};
    int ulen = tvai_get_username(user, (int)sizeof(user));
    printf("username_len=%d username=%s\n", ulen, ulen > 0 ? user : "(none)");
    char dev[1024] = {0};
    int ndev = tvai_device_list(dev, (int)sizeof(dev));
    printf("device_count=%d devices=%s\n", ndev, dev);
    char list[8192] = {0};
    int r = tvai_model_list((char *)"__bogus__", ModelTypeUpscaling, list, (int)sizeof(list));
    printf("model_list_bogus=%d list=%s\n", r, list);
    char list2[8192] = {0};
    int r2 = tvai_model_list((char *)"prob-4", ModelTypeUpscaling, list2, (int)sizeof(list2));
    printf("model_list_prob-4=%d list=%s\n", r2, list2);
    return 0;
}
